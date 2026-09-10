import json
import logging
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.tools import execute_tool
from app.api.schemas import ChatRequest, ChatResponse, Citation, ToolCall, Usage
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import AIRequest
from app.llm.factory import build_provider
from app.rag.prompt import SYSTEM_PROMPT, build_context
from app.rag.citations import unique_citations
from app.rag.retriever import retrieve_relevant_chunks

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)

TOOL_DEFINITIONS = [
    {"type": "function", "function": {"name": "calculate_revenue_growth", "description": "Calculate percentage growth between two revenues.", "parameters": {"type": "object", "properties": {"previous_revenue": {"type": "number"}, "current_revenue": {"type": "number"}}, "required": ["previous_revenue", "current_revenue"]}}},
    {"type": "function", "function": {"name": "calculate_debt_to_ebitda", "description": "Calculate total debt divided by EBITDA.", "parameters": {"type": "object", "properties": {"total_debt": {"type": "number"}, "ebitda": {"type": "number"}}, "required": ["total_debt", "ebitda"]}}},
    {"type": "function", "function": {"name": "calculate_profit_margin", "description": "Calculate net income as a percentage of revenue.", "parameters": {"type": "object", "properties": {"net_income": {"type": "number"}, "revenue": {"type": "number"}}, "required": ["net_income", "revenue"]}}},
]


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    started = time.perf_counter()
    settings = get_settings()
    try:
        provider = build_provider(settings)
        candidates = retrieve_relevant_chunks(db, provider, request.question, top_k=10, document_id=request.document_id)
        context, selected = build_context(candidates, settings.max_context_tokens)
        if not selected:
            raise HTTPException(404, "I couldn't find sufficient evidence in the uploaded documents to answer this question.")
        user_prompt = f"Document context:\n{context}\n\nQuestion: {request.question}"
        response = provider.generate_with_tools(SYSTEM_PROMPT, user_prompt, TOOL_DEFINITIONS)
        calls: list[ToolCall] = []
        for call in response.tool_calls:
            try:
                arguments = json.loads(call["arguments"])
                result = execute_tool(call["tool"], arguments)
            except (json.JSONDecodeError, TypeError, ValueError, KeyError) as exc:
                raise HTTPException(502, "The model returned invalid arguments for a financial calculation.") from exc
            calls.append(ToolCall(tool=call["tool"], arguments=arguments, result=result))
        if calls:
            tool_results = "\n".join(f"Backend tool {call.tool} returned {call.result} for {call.arguments}." for call in calls)
            final_response = provider.generate(SYSTEM_PROMPT, f"{user_prompt}\n\n{tool_results}\nExplain the result and cite the supporting pages.")
            response.text = final_response.text
            response.usage.input_tokens = (response.usage.input_tokens or 0) + (final_response.usage.input_tokens or 0)
            response.usage.output_tokens = (response.usage.output_tokens or 0) + (final_response.usage.output_tokens or 0)
        elapsed = round((time.perf_counter() - started) * 1000)
        citations = unique_citations(selected)
        usage = Usage(model=response.usage.model, input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens, total_tokens=response.usage.total_tokens, retrieved_chunks=len(selected), latency_ms=elapsed)
        db.add(AIRequest(question=request.question, model=usage.model, input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, total_tokens=usage.total_tokens, retrieved_chunks=len(selected), latency_ms=elapsed, response=response.text, metadata_json={"sources": [{"document": citation.document, "page": citation.page} for citation in citations], "tool_calls": [call.model_dump() for call in calls]}))
        db.commit()
        return ChatResponse(answer=response.text, sources=[Citation(document=citation.document, page=citation.page) for citation in citations], tool_calls=calls, usage=usage)
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("Research request failed")
        raise HTTPException(502, "The research request could not be completed. Check the LLM configuration and try again.") from exc
