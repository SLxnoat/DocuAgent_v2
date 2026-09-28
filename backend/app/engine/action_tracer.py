"""Action Tracer for managing session action histories and screenshot persistence."""

import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from playwright.async_api import Page
from app.schemas.action_trace import ActionTrace, DOMElementInfo, ActionType
from app.core.config import settings
from app.core.logging import logger
from app.core.security import sanitize_identifier, mask_sensitive_value


class ActionTracer:
    """Accumulates user interaction events and automatically captures visual snapshots."""

    def __init__(self, session_id: str, page: Page):
        self.session_id = sanitize_identifier(session_id, "session_id")
        self.page = page
        self.traces: List[ActionTrace] = []
        self._action_callbacks: list[Callable] = []
        self.session_dir = settings.SCREENSHOTS_DIR / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def on_action_recorded(self, callback: Callable):
        """Register a callback when an action trace is captured."""
        if callback not in self._action_callbacks:
            self._action_callbacks.append(callback)

    def remove_action_callback(self, callback: Callable):
        """Unregister an action callback."""
        if callback in self._action_callbacks:
            self._action_callbacks.remove(callback)

    async def record_action(
        self,
        action_type: str,
        target_data: Optional[Dict[str, Any]] = None,
        input_value: Optional[str] = None,
        key: Optional[str] = None,
    ) -> ActionTrace:
        """Capture an action, take high-resolution screenshot with element highlighted, and persist."""
        seq_num = len(self.traces) + 1
        action_id = f"act_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow()

        # Parse target element info if present and mask secrets
        dom_info = None
        if target_data:
            try:
                # Mask secret attributes if present
                field_name = (target_data.get("attributes") or {}).get("name") or target_data.get("element_id")
                input_type_val = target_data.get("input_type")
                if input_value:
                    input_value = mask_sensitive_value(field_name, input_type_val, input_value)
                dom_info = DOMElementInfo(**target_data)
            except Exception as e:
                logger.warning(f"Failed to parse DOMElementInfo: {e}")

        # Screenshot capture
        screenshot_filename = f"step_{seq_num:03d}_{action_type}.png"
        screenshot_path = self.session_dir / screenshot_filename
        
        try:
            # Let highlight render cleanly
            await self.page.wait_for_timeout(50)
            await self.page.screenshot(path=str(screenshot_path), full_page=False)
            screenshot_rel_path = f"/storage/screenshots/{self.session_id}/{screenshot_filename}"
        except Exception as e:
            logger.warning(f"Failed to capture screenshot for action {action_id}: {e}")
            screenshot_rel_path = None

        page_title = await self.page.title()
        page_url = self.page.url

        # Normalize ActionType enum
        try:
            enum_action_type = ActionType(action_type.lower())
        except ValueError:
            enum_action_type = ActionType.CLICK

        trace = ActionTrace(
            id=action_id,
            session_id=self.session_id,
            sequence_number=seq_num,
            action_type=enum_action_type,
            timestamp=timestamp,
            page_url=page_url,
            page_title=page_title,
            target_element=dom_info,
            input_value=input_value,
            key=key,
            screenshot_path=str(screenshot_path) if screenshot_rel_path else None,
            screenshot_url=screenshot_rel_path,
        )

        self.traces.append(trace)
        logger.info(f"Recorded action #{seq_num}: [{trace.action_type.value}] on {page_url}")

        if self._action_callbacks:
            for cb in list(self._action_callbacks):
                try:
                    if asyncio.iscoroutinefunction(cb):
                        await cb(trace)
                    else:
                        res = cb(trace)
                        if asyncio.iscoroutine(res):
                            await res
                except Exception as cb_err:
                    logger.debug(f"Action callback error: {cb_err}")

        return trace

    def get_all_traces(self) -> List[ActionTrace]:
        """Return all recorded actions in sequence."""
        return self.traces

    def clear(self):
        """Clear recorded traces."""
        self.traces.clear()
