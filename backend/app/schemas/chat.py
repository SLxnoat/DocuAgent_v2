"""Schemas for Human-in-the-Loop chat refinement requests."""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.document import DocumentationStep


class MessageRole(str, Enum):
    """Chat message role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """A conversational message in the HITL refinement pane."""

    id: str
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    step_number: Optional[int] = None
    applied_changes: Optional[Dict[str, Any]] = None


class ChatRefineRequest(BaseModel):
    """Instruction sent by user to refine or adjust specific sections of a document."""

    document_id: str
    prompt: str = Field(..., description="User refinement request e.g., 'Make step 2 more descriptive'")
    target_step_number: Optional[int] = Field(default=None, description="Optional target step to refine")
    history: List[ChatMessage] = Field(default_factory=list)


class ChatRefineResponse(BaseModel):
    """Response returned after Chat Refiner Agent evaluates and applies edits."""

    document_id: str
    reply_message: str
    updated_steps: List[DocumentationStep] = Field(default_factory=list)
    updated_markdown: str
    modified_step_numbers: List[int] = Field(default_factory=list)
