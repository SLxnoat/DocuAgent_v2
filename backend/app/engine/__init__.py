"""Playwright & CDP Browser Recording Engine."""

try:
    from app.engine.browser_manager import BrowserManager, get_browser_manager
    from app.engine.dom_highlighter import DOMHighlighter
    from app.engine.screencast import ScreencastStreamer
    from app.engine.cdp_listener import CDPEventListener
    from app.engine.action_tracer import ActionTracer
    from app.engine.image_annotator import ImageAnnotator

    __all__ = [
        "BrowserManager",
        "get_browser_manager",
        "DOMHighlighter",
        "ScreencastStreamer",
        "CDPEventListener",
        "ActionTracer",
        "ImageAnnotator",
    ]
except ImportError:
    # Allow individual modules to be imported even if playwright is not present in test environment
    pass

