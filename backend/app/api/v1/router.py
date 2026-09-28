"""Master API v1 Router aggregating all endpoint controllers."""

from fastapi import APIRouter
from app.api.v1.endpoints import sessions, documents, chat, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Recording Sessions"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documentation & Exports"])
api_router.include_router(chat.router, prefix="/chat", tags=["HITL Refinement"])
