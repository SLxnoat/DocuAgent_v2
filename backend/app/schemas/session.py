"""Session schemas for browser recording lifecycle."""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class SessionStatus(str, Enum):
    """Lifecycle states of a recording session."""

    IDLE = "idle"
    STARTING = "starting"
    RECORDING = "recording"
    PAUSED = "paused"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AuthCredentials(BaseModel):
    """Optional basic/form authentication credentials."""

    username: Optional[str] = None
    password: Optional[str] = None
    auth_type: str = Field(default="none", description="none, basic, or form")
    login_url: Optional[str] = None


class SessionCreate(BaseModel):
    """Payload to initialize a new browser recording session."""

    target_url: str = Field(..., description="Target application URL to observe and record")
    title: Optional[str] = Field(default="Untitled Workflow Documentation", description="Workflow title")
    description: Optional[str] = Field(default=None, description="Optional high-level workflow description")
    credentials: Optional[AuthCredentials] = None
    viewport_width: int = Field(default=1440, ge=800, le=3840)
    viewport_height: int = Field(default=900, ge=600, le=2160)
    highlight_color: str = Field(default="#ef4444", description="Hex color code for active element highlight")


class SessionResponse(BaseModel):
    """Response model representing a recording session."""

    id: str
    target_url: str
    title: str
    description: Optional[str] = None
    status: SessionStatus
    action_count: int = 0
    created_at: datetime
    updated_at: datetime
    active_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}
