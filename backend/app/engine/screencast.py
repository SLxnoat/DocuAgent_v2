"""CDP Screencast Streamer for live web workspace visualization."""

import asyncio
from typing import Callable, Optional, Dict, Any
from playwright.async_api import CDPSession, Page
from app.core.config import settings
from app.core.logging import logger


class ScreencastStreamer:
    """Manages CDP Page.startScreencast and forwards interactive user inputs back to the browser."""

    def __init__(self, page: Page, cdp_session: CDPSession):
        self.page = page
        self.cdp_session = cdp_session
        self.is_streaming = False
        self._frame_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def on_frame(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Register a callback when a new screencast frame is emitted from CDP."""
        self._frame_callback = callback

    async def start(self):
        """Start CDP screencast stream."""
        if self.is_streaming:
            return

        self.is_streaming = True

        async def _handle_screencast_frame(params: Dict[str, Any]):
            # Acknowledge frame to CDP session
            try:
                session_id = params.get("sessionId")
                if session_id:
                    await self.cdp_session.send("Page.screencastFrameAck", {"sessionId": session_id})
                
                base64_data = params.get("data")
                metadata = params.get("metadata", {})
                
                if self._frame_callback and base64_data:
                    self._frame_callback(base64_data, metadata)
            except Exception as e:
                logger.debug(f"Error handling screencast frame: {e}")

        self.cdp_session.on("Page.screencastFrame", _handle_screencast_frame)

        await self.cdp_session.send(
            "Page.startScreencast",
            {
                "format": "jpeg",
                "quality": settings.SCREENCAST_QUALITY,
                "maxWidth": settings.PLAYWRIGHT_VIEWPORT_WIDTH,
                "maxHeight": settings.PLAYWRIGHT_VIEWPORT_HEIGHT,
                "everyNthFrame": 1,
            },
        )
        logger.info("CDP Screencast started successfully.")

    async def stop(self):
        """Stop CDP screencast stream."""
        if not self.is_streaming:
            return
        self.is_streaming = False
        try:
            await self.cdp_session.send("Page.stopScreencast")
            logger.info("CDP Screencast stopped.")
        except Exception as e:
            logger.warning(f"Failed to cleanly stop screencast: {e}")

    async def dispatch_mouse_event(self, event_type: str, x: int, y: int, button: str = "left", click_count: int = 1):
        """Forward user mouse events from React canvas into Playwright page."""
        try:
            if event_type == "mousePressed":
                await self.page.mouse.down(button=button)
            elif event_type == "mouseReleased":
                await self.page.mouse.up(button=button)
            elif event_type == "mouseMoved":
                await self.page.mouse.move(x, y)
            elif event_type == "click":
                await self.page.mouse.click(x, y, button=button, click_count=click_count)
        except Exception as e:
            logger.debug(f"Failed to dispatch mouse event: {e}")

    async def dispatch_keyboard_event(self, event_type: str, key: str, text: Optional[str] = None):
        """Forward user keyboard events from React canvas into Playwright page."""
        try:
            if event_type == "keyDown":
                await self.page.keyboard.down(key)
            elif event_type == "keyUp":
                await self.page.keyboard.up(key)
            elif event_type == "type" and text:
                await self.page.keyboard.type(text)
        except Exception as e:
            logger.debug(f"Failed to dispatch keyboard event: {e}")
