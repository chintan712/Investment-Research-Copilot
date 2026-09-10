from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DocumentChunk
from app.llm.base import LLMProvider


@dataclass(frozen=True)
class RetrievedChunk:
    content: str
    document: str
    page: int
    similarity: float


def retrieve_relevant_chunks(db: Session, provider: LLMProvider, query: str, top_k: int = 10, document_id: int | None = None) -> list[RetrievedChunk]:
    query_embedding = provider.embed(query)
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)
    statement = select(DocumentChunk, distance)
    if document_id is not None:
        statement = statement.where(DocumentChunk.document_id == document_id)
    statement = statement.order_by(distance).limit(top_k)
    rows = db.execute(statement).all()
    return [
        RetrievedChunk(chunk.content, chunk.document.filename, chunk.page_number, 1 - float(distance_value))
        for chunk, distance_value in rows
    ]
