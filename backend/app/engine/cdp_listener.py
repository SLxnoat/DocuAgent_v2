"""CDP Event Listener for fine-grained network, DOM, and user events."""

import asyncio
from typing import Callable, Dict, Any, Optional
from playwright.async_api import CDPSession, Page
from app.core.logging import logger


class CDPEventListener:
    """Listens to low-level CDP domains (DOM, Page, Network, Runtime) to supplement DOM traces."""

    def __init__(self, page: Page, cdp_session: CDPSession):
        self.page = page
        self.cdp_session = cdp_session
        self._navigation_callbacks: list[Callable[[str], None]] = []

    async def initialize(self):
        """Enable necessary CDP domains."""
        try:
            await self.cdp_session.send("Page.enable")
            await self.cdp_session.send("DOM.enable")
            await self.cdp_session.send("Runtime.enable")
            
            self.cdp_session.on("Page.frameNavigated", self._handle_navigation)
            logger.info("CDP Event Listener initialized.")
        except Exception as e:
            logger.error(f"Failed to enable CDP domains: {e}")

    def on_navigation(self, callback: Callable[[str], None]):
        """Register a callback for page navigations."""
        self._navigation_callbacks.append(callback)

    def _handle_navigation(self, params: Dict[str, Any]):
        """Triggered on page frame navigation."""
        frame = params.get("frame", {})
        url = frame.get("url")
        if url and not url.startswith("about:"):
            logger.debug(f"CDP Navigation detected: {url}")
            for cb in self._navigation_callbacks:
                cb(url)
