from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import RequestResponse
from app.db.database import get_db
from app.db.models import AIRequest

router = APIRouter(prefix="/requests", tags=["requests"])


@router.get("", response_model=list[RequestResponse])
def list_requests(db: Session = Depends(get_db)) -> list[AIRequest]:
    return db.query(AIRequest).order_by(AIRequest.timestamp.desc()).limit(100).all()
