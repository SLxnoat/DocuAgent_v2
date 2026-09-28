"""LangGraph Dynamic Multi-Agent State definitions for DocuAgent AI."""

from typing import TypedDict, List, Dict, Any, Optional


class DocuAgentState(TypedDict):
    """Global dynamic state flowing through the autonomous LangGraph multi-agent network."""

    session_id: str
    target_url: str
    raw_action_traces: List[Dict[str, Any]]
    
    # Dynamic Multi-Agent Orchestration & Control
    next_agent: Optional[str]  # intent_parser, technical_writer, quality_reviewer, chat_refiner, FINISH
    supervisor_directives: Optional[str]  # Dynamic instructions passed from supervisor to next agent
    iteration_count: int  # Dynamic loop counter
    agent_activity_log: List[Dict[str, Any]]  # Multi-agent conversation/step history
    
    # 1. Intent Parser Output
    workflow_intent: Optional[str]
    grouped_steps: Optional[List[Dict[str, Any]]]

    # 2. Screenshot Agent Output (Visual Assets & Annotations)
    visual_assets: Optional[List[Dict[str, Any]]]
    visual_processing_status: Optional[str]

    # 3. Technical Writer Output
    synthesized_steps: Optional[List[Dict[str, Any]]]
    executive_summary: Optional[str]
    prerequisites: Optional[List[str]]
    raw_markdown: Optional[str]

    # 4. Quality Reviewer Output
    quality_report: Optional[Dict[str, Any]]
    review_iteration: int
    is_approved: bool

    # 5. Chat Refiner HITL State
    user_instruction: Optional[str]
    target_step_number: Optional[int]
    refinement_history: Optional[List[Dict[str, Any]]]

    # Error state & metadata
    error_message: Optional[str]
    metadata: Dict[str, Any]
