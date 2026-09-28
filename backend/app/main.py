"""FastAPI Main Application Entrypoint for DocuAgent AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.v1.router import api_router
from app.api.websockets.browser_stream import router as screencast_ws_router
from app.api.websockets.session_events import router as events_ws_router
from app.engine.browser_manager import get_browser_manager
from app.storage.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events management for startup and shutdown."""
    setup_logging()
    logger.info("Initializing DocuAgent AI Backend Orchestrator...")
    
    # Initialize DB schemas
    await init_db()
    
    # Initialize global browser manager
    browser_manager = get_browser_manager()
    await browser_manager.initialize()
    
    yield
    
    logger.info("Shutting down DocuAgent AI Backend Orchestrator...")
    await browser_manager.shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="DocuAgent AI — Autonomous Technical Documentation Engine with Live Browser Recording & LangGraph",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files for Screenshots & Export Artifacts
app.mount("/storage", StaticFiles(directory=str(settings.STORAGE_DIR)), name="storage")

# REST API & WebSocket Routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(screencast_ws_router)
app.include_router(events_ws_router)


@app.get("/")
async def root():
    """Root entrypoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
    }
