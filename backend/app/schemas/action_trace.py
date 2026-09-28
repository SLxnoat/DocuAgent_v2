"""Schemas for DOM interactions, CDP events, and action traces."""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Types of captured DOM and user interactions."""

    CLICK = "click"
    DBLCLICK = "dblclick"
    INPUT = "input"
    CHANGE = "change"
    SELECT = "select"
    SUBMIT = "submit"
    KEYPRESS = "keypress"
    NAVIGATION = "navigation"
    SCROLL = "scroll"
    HOVER = "hover"


class BoundingBox(BaseModel):
    """Element coordinate bounding box."""

    x: float
    y: float
    width: float
    height: float
    top: float = 0
    left: float = 0
    bottom: float = 0
    right: float = 0


class DOMElementInfo(BaseModel):
    """Detailed DOM element metadata for technical writer reasoning."""

    tag_name: str
    element_id: Optional[str] = None
    class_names: List[str] = Field(default_factory=list)
    css_selector: str
    xpath: Optional[str] = None
    inner_text: Optional[str] = None
    placeholder: Optional[str] = None
    aria_label: Optional[str] = None
    role: Optional[str] = None
    input_type: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    attributes: Dict[str, str] = Field(default_factory=dict)


class ActionTrace(BaseModel):
    """Standardized recorded user action."""

    id: str
    session_id: str
    sequence_number: int
    action_type: ActionType
    timestamp: datetime
    page_url: str
    page_title: str
    target_element: Optional[DOMElementInfo] = None
    input_value: Optional[str] = None
    key: Optional[str] = None
    screenshot_path: Optional[str] = None
    screenshot_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
