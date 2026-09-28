"""Application Configuration via Pydantic Settings."""

from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """DocuAgent Settings schema."""

    # Project metadata
    PROJECT_NAME: str = "DocuAgent AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_SECRET_KEY: str = "docuagent-insecure-secret-key-change-in-production"

    # Server & CORS
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # LLM & Multi-Agent Stack
    LLM_PROVIDER: str = "ollama_cloud"  # ollama_cloud, ollama_local, openai, litellm
    OLLAMA_BASE_URL: str = "https://ollama.com/api"
    OLLAMA_API_KEY: str = ""
    DEFAULT_MODEL: str = "llama3.3:70b"
    FAST_MODEL: str = "llama3.1:8b"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Playwright & Screencast
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_VIEWPORT_WIDTH: int = 1440
    PLAYWRIGHT_VIEWPORT_HEIGHT: int = 900
    PLAYWRIGHT_HIGHLIGHT_COLOR: str = "#ef4444"
    PLAYWRIGHT_HIGHLIGHT_OUTLINE_WIDTH: str = "4px"
    SCREENCAST_FPS: int = 15
    SCREENCAST_QUALITY: int = 80

    # Paths and Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "data" / "storage"
    SCREENSHOTS_DIR: Path = BASE_DIR / "data" / "storage" / "screenshots"
    EXPORTS_DIR: Path = BASE_DIR / "data" / "storage" / "exports"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/docuagent.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()

# Ensure directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
