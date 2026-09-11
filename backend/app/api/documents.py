import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.schemas import DocumentResponse
from app.core.config import get_settings
from app.db.database import get_db
from app.db.models import Document, DocumentChunk
from app.documents.chunker import chunk_document
from app.documents.parser import InvalidPDFError, extract_pages
from app.llm.factory import build_provider

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    document_type: str | None = None,
    db: Session = Depends(get_db),
) -> Document:
    settings = get_settings()
    if file.content_type != "application/pdf":
        raise HTTPException(415, "Only PDF uploads are supported")
    #check for duplicate filename in the database
    filename = file.filename or "document.pdf"
    if db.query(Document).filter(Document.filename == filename).first():
        raise HTTPException(409, f"A document named '{filename}' already exists")

    data = file.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(413, "The uploaded file is too large")
    try:
        pages = extract_pages(data)
        chunks = chunk_document(pages)
        provider = build_provider(settings)
        document = Document(filename=file.filename or "document.pdf", document_type=document_type)
        db.add(document)
        db.flush()
        for chunk in chunks:
            db.add(DocumentChunk(document_id=document.id, page_number=chunk.page_number, chunk_index=chunk.chunk_index, content=chunk.content, embedding=provider.embed(chunk.content)))
        db.commit()
        db.refresh(document)
        return document
    except (InvalidPDFError, RuntimeError, ValueError) as exc:
        db.rollback()
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        db.rollback()
        logger.exception("Document ingestion failed")
        raise HTTPException(502, "Document ingestion could not contact the embedding provider.") from exc

@router.delete("/{document_id}", status_code=204)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> None:
    document = db.query(Document).filter(Document.id == document_id).first()
    if document is None:
        raise HTTPException(404, "Document not found")

    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    db.delete(document)
    db.commit()

@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)) -> list[Document]:
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()
