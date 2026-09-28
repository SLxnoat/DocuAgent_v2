"""Schemas for System Settings and Live Model Integrator Status."""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LLMProviderType(str, Enum):
    """Supported LLM provider backends."""

    OLLAMA_CLOUD = "ollama_cloud"
    OLLAMA_LOCAL = "ollama_local"
    OPENAI = "openai"
    LITELLM = "litellm"
    ANTHROPIC = "anthropic"


class SettingsConfig(BaseModel):
    """System configuration schema."""

    # LLM Settings
    llm_provider: str = Field(default="ollama_cloud")
    ollama_base_url: str = Field(default="https://ollama.com/api")
    ollama_api_key_masked: Optional[str] = None
    default_model: str = Field(default="llama3.3:70b")
    fast_model: str = Field(default="llama3.1:8b")
    openai_api_key_masked: Optional[str] = None

    # Browser & Highlight Settings
    highlight_color: str = Field(default="#ef4444")
    highlight_outline_width: str = Field(default="4px")
    viewport_width: int = Field(default=1440)
    viewport_height: int = Field(default=900)
    screencast_fps: int = Field(default=15)
    screencast_quality: int = Field(default=80)

    # Export & General
    default_export_format: str = Field(default="pdf")
    environment: str = Field(default="development")
    backend_port: int = Field(default=8030)


class SettingsUpdate(BaseModel):
    """Payload to update runtime settings."""

    llm_provider: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_api_key: Optional[str] = None
    default_model: Optional[str] = None
    fast_model: Optional[str] = None
    openai_api_key: Optional[str] = None

    highlight_color: Optional[str] = None
    highlight_outline_width: Optional[str] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    screencast_fps: Optional[int] = None
    screencast_quality: Optional[int] = None


class ModelTestRequest(BaseModel):
    """Payload to test connection with specific LLM parameters."""

    provider: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None


class ModelStatusResponse(BaseModel):
    """Live status and heartbeat telemetry of the LLM model integrator."""

    status: str = Field(..., description="online, degraded, offline, checking")
    provider: str
    model_name: str
    latency_ms: Optional[float] = None
    last_ping: str
    message: str
    capabilities: List[str] = Field(default_factory=list)


class ModelTestResponse(BaseModel):
    """Response returned after running a live model connection test."""

    success: bool
    latency_ms: float
    provider: str
    model_name: str
    sample_response: Optional[str] = None
    error_message: Optional[str] = None
