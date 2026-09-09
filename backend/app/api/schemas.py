from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document: str
    page: int


class ToolCall(BaseModel):
    tool: str
    arguments: dict[str, Any]
    result: float


class Usage(BaseModel):
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    retrieved_chunks: int = 0
    latency_ms: int = 0


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[Citation]
    tool_calls: list[ToolCall]
    usage: Usage


class DocumentResponse(BaseModel):
    id: int
    filename: str
    document_type: str | None
    uploaded_at: datetime


class RequestResponse(BaseModel):
    id: int
    timestamp: datetime
    question: str
    model: str | None
    total_tokens: int | None
    retrieved_chunks: int
    latency_ms: int
    response: str
