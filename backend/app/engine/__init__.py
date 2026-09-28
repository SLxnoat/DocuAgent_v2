"""Playwright & CDP Browser Recording Engine."""

from app.engine.browser_manager import BrowserManager, get_browser_manager
from app.engine.dom_highlighter import DOMHighlighter
from app.engine.screencast import ScreencastStreamer
from app.engine.cdp_listener import CDPEventListener
from app.engine.action_tracer import ActionTracer

__all__ = [
    "BrowserManager",
    "get_browser_manager",
    "DOMHighlighter",
    "ScreencastStreamer",
    "CDPEventListener",
    "ActionTracer",
]
