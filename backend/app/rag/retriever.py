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


def retrieve_relevant_chunks(db: Session, provider: LLMProvider, query: str, top_k: int = 10) -> list[RetrievedChunk]:
    query_embedding = provider.embed(query)
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)
    rows = db.execute(select(DocumentChunk, distance).order_by(distance).limit(top_k)).all()
    return [
        RetrievedChunk(chunk.content, chunk.document.filename, chunk.page_number, 1 - float(distance_value))
        for chunk, distance_value in rows
    ]
