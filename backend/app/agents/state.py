"""LangGraph State definitions for multi-agent documentation generation."""

from typing import TypedDict, List, Dict, Any, Optional
from app.schemas.action_trace import ActionTrace
from app.schemas.document import DocumentationStep, QualityReport, DocumentSchema


class DocuAgentState(TypedDict):
    """Global state flowing through the LangGraph pipeline."""

    session_id: str
    target_url: str
    raw_action_traces: List[Dict[str, Any]]
    
    # 1. Intent Parser Output
    workflow_intent: Optional[str]
    grouped_steps: Optional[List[Dict[str, Any]]]
    
    # 2. Technical Writer Output
    synthesized_steps: Optional[List[Dict[str, Any]]]
    executive_summary: Optional[str]
    prerequisites: Optional[List[str]]
    raw_markdown: Optional[str]
    
    # 3. Quality Reviewer Output
    quality_report: Optional[Dict[str, Any]]
    review_iteration: int
    is_approved: bool
    
    # 4. Chat Refiner HITL State
    user_instruction: Optional[str]
    target_step_number: Optional[int]
    refinement_history: Optional[List[Dict[str, Any]]]
    
    # Error state & metadata
    error_message: Optional[str]
    metadata: Dict[str, Any]
