"""Visual Annotation and Focus Crop Tools for CrewAI and Hybrid multi-agent execution."""

import json
from typing import List, Dict, Any, Optional, Type, Union
from pydantic import BaseModel, Field
from app.engine.image_annotator import ImageAnnotator
from app.core.config import settings

try:
    from crewai.tools import BaseTool as CrewAIBaseTool
except ImportError:
    CrewAIBaseTool = object


class ImageAnnotatorInput(BaseModel):
    """Input schema for ImageAnnotatorTool."""

    session_id: str = Field(description="Active recording session identifier")
    step_number: int = Field(description="Sequential step number for badge label")
    step_data: Dict[str, Any] = Field(description="Step dictionary containing goal, action type, screenshot path")
    raw_traces: List[Dict[str, Any]] = Field(default_factory=list, description="Raw action traces from session")
    highlight_color: Optional[str] = Field(default=None, description="Hex color for highlight outline and badge")


class ImageAnnotatorTool(CrewAIBaseTool if CrewAIBaseTool is not object else BaseModel):
    """Tool that calculates element coordinates, renders glowing outlines, and stamps numbered step badges."""

    name: str = "ImageAnnotatorTool"
    description: str = (
        "Calculates target element bounding box coordinates on full-viewport screenshots, "
        "draws neon/red highlight outlines, attaches numbered circular callout badges, "
        "redacts sensitive inputs, and produces production-ready SOP screenshot assets."
    )
    args_schema: Type[BaseModel] = ImageAnnotatorInput

    def annotate_step(
        self,
        session_id: str,
        step_number: int,
        step_data: Dict[str, Any],
        raw_traces: List[Dict[str, Any]],
        highlight_color: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Run image annotation engine on a procedural step."""
        color = highlight_color or settings.PLAYWRIGHT_HIGHLIGHT_COLOR
        annotator = ImageAnnotator(session_id=session_id)
        return annotator.process_step_image(
            step_number=step_number,
            step_data=step_data,
            raw_traces=raw_traces,
            highlight_color=color,
        )

    def _run(
        self,
        session_id: str,
        step_number: int,
        step_data: Dict[str, Any],
        raw_traces: List[Dict[str, Any]],
        highlight_color: Optional[str] = None,
    ) -> str:
        """Execution method for CrewAI / LangChain."""
        asset = self.annotate_step(
            session_id=session_id,
            step_number=step_number,
            step_data=step_data,
            raw_traces=raw_traces,
            highlight_color=highlight_color,
        )
        return json.dumps(asset or {"status": "no_image_generated"}, indent=2)

    def run(
        self,
        session_id: str,
        step_number: int,
        step_data: Dict[str, Any],
        raw_traces: List[Dict[str, Any]],
        highlight_color: Optional[str] = None,
    ) -> str:
        """Public invocation wrapper."""
        return self._run(
            session_id=session_id,
            step_number=step_number,
            step_data=step_data,
            raw_traces=raw_traces,
            highlight_color=highlight_color,
        )


class FocusCropInput(BaseModel):
    """Input schema for FocusCropTool."""

    session_id: str = Field(description="Active recording session identifier")
    step_number: int = Field(description="Step number")
    step_data: Dict[str, Any] = Field(description="Step metadata")
    raw_traces: List[Dict[str, Any]] = Field(default_factory=list, description="Raw action traces")


class FocusCropTool(CrewAIBaseTool if CrewAIBaseTool is not object else BaseModel):
    """Tool that generates focused 420x260 crop thumbnails centered on the target interaction element."""

    name: str = "FocusCropTool"
    description: str = (
        "Generates focused 420x260 crop thumbnails centered around the exact target UI element coordinates "
        "with balanced padding for quick visual scanning."
    )
    args_schema: Type[BaseModel] = FocusCropInput

    def _run(
        self,
        session_id: str,
        step_number: int,
        step_data: Dict[str, Any],
        raw_traces: List[Dict[str, Any]],
    ) -> str:
        annotator = ImageAnnotator(session_id=session_id)
        asset = annotator.process_step_image(
            step_number=step_number,
            step_data=step_data,
            raw_traces=raw_traces,
        )
        focus_url = asset.get("focus_crop_url") if asset else None
        return json.dumps({"step_number": step_number, "focus_crop_url": focus_url}, indent=2)

    def run(
        self,
        session_id: str,
        step_number: int,
        step_data: Dict[str, Any],
        raw_traces: List[Dict[str, Any]],
    ) -> str:
        return self._run(
            session_id=session_id,
            step_number=step_number,
            step_data=step_data,
            raw_traces=raw_traces,
        )
