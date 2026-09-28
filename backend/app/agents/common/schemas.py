"""Pydantic schemas and data contracts for Hybrid LangGraph-CrewAI agents."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.document import CalloutType


class ParsedStepTrace(BaseModel):
    """Structured step representation parsed from raw telemetry action traces."""

    step_number: int = Field(description="Sequential 1-indexed step number")
    title: str = Field(description="Action-oriented concise step title (e.g., 'Click Submit Button')")
    goal: str = Field(description="User intent or goal behind this group of actions")
    raw_action_ids: List[str] = Field(default_factory=list, description="IDs of raw traces included in this step")
    primary_action: str = Field(description="Primary interaction type: click, input, navigate, submit")
    target_element_desc: str = Field(description="Human-readable description of target UI element")
    input_value: Optional[str] = Field(default=None, description="Input string value entered, if applicable")
    screenshot_path: Optional[str] = Field(default=None, description="Path or URL to the key screenshot")


class ParsedTelemetryResult(BaseModel):
    """Result of Intent & Telemetry Parsing micro-crew."""

    workflow_intent: str = Field(description="Overall workflow objective detected from traces")
    grouped_steps: List[ParsedStepTrace] = Field(default_factory=list, description="List of grouped procedural steps")


class SynthesizedCallout(BaseModel):
    """Callout block within a synthesized step."""

    type: CalloutType = Field(default=CalloutType.NOTE, description="note, tip, warning, or important")
    content: str = Field(description="Callout text body")


class SynthesizedStepItem(BaseModel):
    """Synthesized technical manual step with instructions and visual assets."""

    step_number: int = Field(description="Sequential 1-indexed step number")
    title: str = Field(description="Concise, action-oriented step title")
    instruction: str = Field(description="Clear, authoritative imperative instruction")
    detailed_description: Optional[str] = Field(default=None, description="Contextual explanation of what happens")
    target_ui_element: Optional[str] = Field(default=None, description="Target UI element name or label")
    action_type: Optional[str] = Field(default=None, description="click, input, select, etc.")
    input_value_used: Optional[str] = Field(default=None, description="Input value used if applicable")
    screenshot_url: Optional[str] = Field(default=None, description="URL of primary screenshot")
    annotated_screenshot_url: Optional[str] = Field(default=None, description="URL of screenshot with outline & badges")
    focus_crop_url: Optional[str] = Field(default=None, description="URL of focused element crop thumbnail")
    callouts: List[SynthesizedCallout] = Field(default_factory=list, description="List of tip/warning callouts")
    raw_action_ids: List[str] = Field(default_factory=list, description="Referenced raw telemetry action IDs")


class SynthesizedManualResult(BaseModel):
    """Result of Visual & Technical Authoring micro-crew."""

    workflow_intent: str = Field(description="Refined workflow title")
    executive_summary: str = Field(description="High-level overview of the manual")
    prerequisites: List[str] = Field(default_factory=list, description="Requirements before starting the procedure")
    synthesized_steps: List[SynthesizedStepItem] = Field(default_factory=list, description="Synthesized steps")
    raw_markdown: str = Field(description="Full GitHub-flavored Markdown text")


class QualityScorecard(BaseModel):
    """Structured QA audit evaluation report emitted by the QA & Compliance micro-crew."""

    score: float = Field(ge=0.0, le=100.0, description="Overall quality score percentage (0-100)")
    is_approved: bool = Field(default=True, description="True if score >= 85 and no critical blockers")
    completeness_score: float = Field(default=100.0, description="Score evaluating missing steps or details")
    clarity_score: float = Field(default=100.0, description="Score evaluating instruction clarity and tone")
    structure_score: float = Field(default=100.0, description="Score evaluating formatting, headings, and callouts")
    strengths: List[str] = Field(default_factory=list, description="Positive aspects identified in documentation")
    suggestions: List[str] = Field(default_factory=list, description="Actionable revision recommendations")
    missing_items: List[str] = Field(default_factory=list, description="Identified gaps or missing instructions")


class RefinementResult(BaseModel):
    """Result of Human-in-the-Loop Conversational Refinement micro-crew."""

    reply_message: str = Field(description="Assistant conversational response to the user's feedback")
    modified_step_numbers: List[int] = Field(default_factory=list, description="List of step numbers modified")
    updated_steps: List[Dict[str, Any]] = Field(default_factory=list, description="Full list of updated steps")
    updated_markdown: str = Field(description="Full updated raw markdown document")
