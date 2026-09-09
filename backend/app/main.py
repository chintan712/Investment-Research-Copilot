from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.chat import router as chat_router
from app.api.documents import router as documents_router
from app.api.requests import router as requests_router


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(requests_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
