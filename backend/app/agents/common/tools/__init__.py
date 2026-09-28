"""Custom Pydantic-validated tools for CrewAI and Hybrid multi-agent execution."""

from app.agents.common.tools.dom_parser import DOMTraceParserTool
from app.agents.common.tools.image_annotator import ImageAnnotatorTool, FocusCropTool
from app.agents.common.tools.markdown_qa import MarkdownValidatorTool, QualityScoreCalculatorTool

__all__ = [
    "DOMTraceParserTool",
    "ImageAnnotatorTool",
    "FocusCropTool",
    "MarkdownValidatorTool",
    "QualityScoreCalculatorTool",
]
