"""DOM and Telemetry Parsing Tool for analyzing and cleaning browser CDP action traces."""

import json
from typing import List, Dict, Any, Optional, Type, Union
from pydantic import BaseModel, Field

try:
    from crewai.tools import BaseTool as CrewAIBaseTool
except ImportError:
    CrewAIBaseTool = object  # Fallback if crewai is not installed yet


class DOMTraceParserInput(BaseModel):
    """Input schema for DOMTraceParserTool."""

    raw_traces: Union[List[Dict[str, Any]], str] = Field(
        description="List of raw CDP interaction traces or JSON string of traces"
    )
    filter_noise: bool = Field(
        default=True,
        description="Whether to de-noise redundant micro-scrolls and unfocused hovers",
    )


class DOMTraceParserTool(CrewAIBaseTool if CrewAIBaseTool is not object else BaseModel):
    """Tool that parses, de-noises, and clusters raw browser CDP telemetry into structured steps."""

    name: str = "DOMTraceParserTool"
    description: str = (
        "Parses raw browser CDP telemetry logs, filters out noise (empty scrolls, redundant hovers), "
        "clusters repeated keystrokes into single input actions, extracts human-readable target labels, "
        "and flags sensitive inputs (passwords/PII)."
    )
    args_schema: Type[BaseModel] = DOMTraceParserInput

    def _clean_element_description(self, elem: Optional[Dict[str, Any]]) -> str:
        """Derive a friendly, concise label for the UI target element."""
        if not elem:
            return "UI Element"

        # 1. Direct visible text or aria-label
        inner_text = (elem.get("inner_text") or "").strip()
        aria_label = (elem.get("aria_label") or "").strip()
        placeholder = (elem.get("placeholder") or "").strip()
        elem_id = (elem.get("element_id") or "").strip()
        tag_name = (elem.get("tag_name") or "element").lower()

        if aria_label:
            return f"'{aria_label}' {tag_name}"
        if inner_text and len(inner_text) <= 40:
            return f"'{inner_text}' {tag_name}"
        if placeholder:
            return f"'{placeholder}' field"
        if elem_id and not elem_id.startswith(":r") and not elem_id.startswith("headlessui"):
            return f"#{elem_id} {tag_name}"

        # 2. Extract selector segment
        selector = elem.get("css_selector") or ""
        if selector:
            parts = [p.strip() for p in selector.split(">") if p.strip()]
            if parts:
                return f"{parts[-1]} element"

        return f"{tag_name} element"

    def _is_sensitive_element(self, elem: Optional[Dict[str, Any]]) -> bool:
        """Detect if element handles sensitive credentials, tokens, or PII."""
        if not elem:
            return False
        input_type = (elem.get("input_type") or "").lower()
        if input_type in ("password", "token", "secret", "cvv", "pin"):
            return True
        
        # Check attributes and labels
        attrs = elem.get("attributes") or {}
        name = (attrs.get("name") or "").lower()
        elem_id = (elem.get("element_id") or "").lower()
        for kw in ("password", "secret", "cvv", "creditcard", "ssn"):
            if kw in name or kw in elem_id:
                return True
        return False

    def parse_traces(
        self,
        raw_traces: Union[List[Dict[str, Any]], str],
        filter_noise: bool = True,
    ) -> Dict[str, Any]:
        """Core parsing and de-noising algorithm."""
        if isinstance(raw_traces, str):
            try:
                traces = json.loads(raw_traces)
            except Exception:
                traces = []
        else:
            traces = raw_traces or []

        if not traces:
            return {
                "workflow_intent": "General Workflow",
                "total_raw_traces": 0,
                "parsed_steps_count": 0,
                "grouped_steps": [],
            }

        # 1. Denoise and coalesce interactions
        coalesced_traces: List[Dict[str, Any]] = []
        for t in traces:
            action_type = (t.get("action_type") or "").lower()

            if filter_noise:
                # Discard solitary hovers unless explicit
                if action_type in ("hover", "mousemove"):
                    continue
                # Discard non-meaningful scroll events
                if action_type == "scroll":
                    continue

            # Combine consecutive input / change events on the same target selector
            if coalesced_traces and action_type in ("input", "change", "keypress"):
                prev = coalesced_traces[-1]
                prev_action = (prev.get("action_type") or "").lower()
                prev_elem = prev.get("target_element") or {}
                curr_elem = t.get("target_element") or {}
                
                same_selector = (
                    prev_elem.get("css_selector")
                    and prev_elem.get("css_selector") == curr_elem.get("css_selector")
                )
                if prev_action in ("input", "change", "keypress") and same_selector:
                    # Update previous step with latest input value and screenshot
                    if t.get("input_value") is not None:
                        prev["input_value"] = t.get("input_value")
                    if t.get("screenshot_url"):
                        prev["screenshot_url"] = t.get("screenshot_url")
                        prev["screenshot_path"] = t.get("screenshot_path")
                    if "raw_action_ids" in prev and t.get("id"):
                        prev["raw_action_ids"].append(t.get("id"))
                    continue

            trace_copy = dict(t)
            trace_copy["raw_action_ids"] = [t.get("id")] if t.get("id") else []
            coalesced_traces.append(trace_copy)

        # 2. Cluster into structured steps
        grouped_steps: List[Dict[str, Any]] = []
        for idx, item in enumerate(coalesced_traces, 1):
            action = (item.get("action_type") or "interact").lower()
            elem = item.get("target_element") or {}
            target_desc = self._clean_element_description(elem)
            is_sensitive = self._is_sensitive_element(elem)
            page_title = item.get("page_title") or "Target Page"
            input_val = item.get("input_value")

            if is_sensitive and input_val:
                input_val = "•••••••• [REDACTED]"

            # Formulate action-oriented title
            if action == "click":
                title = f"Click {target_desc}"
                goal = f"Click on {target_desc} on {page_title}"
            elif action in ("input", "change"):
                if input_val and not is_sensitive:
                    title = f"Enter '{input_val}' into {target_desc}"
                else:
                    title = f"Fill in {target_desc}"
                goal = f"Provide requested input in {target_desc}"
            elif action == "submit":
                title = f"Submit {target_desc}"
                goal = f"Submit the form via {target_desc}"
            elif action == "navigation":
                title = f"Navigate to {item.get('page_url') or page_title}"
                goal = f"Open and load {page_title}"
            else:
                title = f"{action.capitalize()} {target_desc}"
                goal = f"Perform {action} on {target_desc}"

            step_entry = {
                "step_number": idx,
                "title": title,
                "goal": goal,
                "raw_action_ids": item.get("raw_action_ids", []),
                "primary_action": action,
                "target_element_desc": target_desc,
                "input_value": input_val,
                "is_sensitive": is_sensitive,
                "page_url": item.get("page_url"),
                "page_title": page_title,
                "screenshot_url": item.get("screenshot_url"),
                "screenshot_path": item.get("screenshot_path"),
            }
            grouped_steps.append(step_entry)

        # Detect high-level workflow intent from pages visited
        pages = list(dict.fromkeys([s.get("page_title") for s in grouped_steps if s.get("page_title")]))
        workflow_intent = f"Standard Operating Procedure for {pages[0]}" if pages else "Application Workflow Manual"

        return {
            "workflow_intent": workflow_intent,
            "total_raw_traces": len(traces),
            "parsed_steps_count": len(grouped_steps),
            "grouped_steps": grouped_steps,
        }

    def _run(
        self,
        raw_traces: Union[List[Dict[str, Any]], str],
        filter_noise: bool = True,
    ) -> str:
        """Execution method for CrewAI / LangChain tool invocation."""
        result = self.parse_traces(raw_traces=raw_traces, filter_noise=filter_noise)
        return json.dumps(result, indent=2)

    def run(
        self,
        raw_traces: Union[List[Dict[str, Any]], str],
        filter_noise: bool = True,
    ) -> str:
        """Public invocation wrapper."""
        return self._run(raw_traces=raw_traces, filter_noise=filter_noise)
