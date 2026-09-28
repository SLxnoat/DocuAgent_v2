"""Pydantic schemas for DocuAgent data structures."""

from app.schemas.session import SessionCreate, SessionResponse, SessionStatus
from app.schemas.action_trace import ActionTrace, DOMElementInfo, ActionType
from app.schemas.document import DocumentSchema, DocumentationStep, ExportRequest
from app.schemas.chat import ChatMessage, ChatRefineRequest, ChatRefineResponse

__all__ = [
    "SessionCreate",
    "SessionResponse",
    "SessionStatus",
    "ActionTrace",
    "DOMElementInfo",
    "ActionType",
    "DocumentSchema",
    "DocumentationStep",
    "ExportRequest",
    "ChatMessage",
    "ChatRefineRequest",
    "ChatRefineResponse",
]
