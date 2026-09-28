"""Custom domain exceptions for DocuAgent AI."""

from typing import Any, Optional


class DocuAgentException(Exception):
    """Base exception for DocuAgent system."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.details = details


class SessionNotFoundError(DocuAgentException):
    """Raised when a recording session is not found."""


class BrowserSessionError(DocuAgentException):
    """Raised when Playwright or CDP encounters a runtime failure."""


class AgentPipelineError(DocuAgentException):
    """Raised when LangGraph multi-agent execution fails."""


class ExportError(DocuAgentException):
    """Raised when PDF/HTML generation encounters an error."""
