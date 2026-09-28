"""Application Configuration via Pydantic Settings."""

from pathlib import Path
from typing import Any, List
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
    BACKEND_PORT: int = 8030
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

    # Multi-Agent Orchestration Stack
    AGENT_ORCHESTRATOR: str = "hybrid"  # hybrid, crewai, langgraph
    CREWAI_PROCESS_MODE: str = "sequential"  # sequential, hierarchical
    MAX_REVISION_LOOPS: int = 3
    QUALITY_THRESHOLD_SCORE: int = 85

    # LLM & Multi-Agent Stack
    LLM_PROVIDER: str = "ollama_local"  # ollama_cloud, ollama_local, openai, litellm
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_API_KEY: str = ""
    DEFAULT_MODEL: str = "qwen2.5:7b"
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


def sync_env_file(updates: dict[str, Any]) -> bool:
    """Safely update or append keys in root .env file.

    Values containing shell-special characters (spaces, colons in URLs,
    JSON brackets, etc.) are automatically wrapped in double-quotes so
    the .env file remains valid on re-read.
    """
    import re

    env_path = settings.BASE_DIR / ".env"
    if not env_path.exists():
        example_path = settings.BASE_DIR / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text("# DocuAgent AI Configuration\n", encoding="utf-8")

    def _format_value(val: str) -> str:
        """Wrap value in double-quotes if it contains special characters."""
        if val == "":
            return ""
        # Quote URLs, JSON arrays, values with spaces/hashes/equals
        if re.search(r'[\s:/?=&#\[\]{}]', val):
            escaped = val.replace('"', '\\"')
            return f'"{escaped}"'
        return val

    lines = env_path.read_text(encoding="utf-8").splitlines()
    updated_keys: set = set()
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                val = updates[key]
                str_val = str(val) if val is not None else ""
                new_lines.append(f"{key}={_format_value(str_val)}")
                updated_keys.add(key)
                continue
        new_lines.append(line)

    # Append any new keys not already in the file
    for key, val in updates.items():
        if key not in updated_keys:
            str_val = str(val) if val is not None else ""
            new_lines.append(f"{key}={_format_value(str_val)}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True
