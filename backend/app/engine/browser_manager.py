"""Playwright Browser Manager orchestrating browser lifecycles and CDP bindings."""

import asyncio
from typing import Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, CDPSession
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import BrowserSessionError
from app.schemas.session import SessionCreate, SessionStatus
from app.engine.dom_highlighter import DOMHighlighter
from app.engine.screencast import ScreencastStreamer
from app.engine.cdp_listener import CDPEventListener
from app.engine.action_tracer import ActionTracer


class ActiveBrowserSession:
    """Encapsulates all resources and controllers for a single recording session."""

    def __init__(
        self,
        session_id: str,
        context: BrowserContext,
        page: Page,
        cdp_session: CDPSession,
        screencaster: ScreencastStreamer,
        cdp_listener: CDPEventListener,
        tracer: ActionTracer,
        target_url: str,
        highlight_color: str,
    ):
        self.session_id = session_id
        self.context = context
        self.page = page
        self.cdp_session = cdp_session
        self.screencaster = screencaster
        self.cdp_listener = cdp_listener
        self.tracer = tracer
        self.target_url = target_url
        self.highlight_color = highlight_color
        self.status = SessionStatus.RECORDING


class BrowserManager:
    """Global manager for Playwright browser instance and active sessions."""

    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, ActiveBrowserSession] = {}
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Start Playwright and launch global Chromium browser."""
        if self._browser is None:
            logger.info("Initializing Playwright Chromium instance...")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=settings.PLAYWRIGHT_HEADLESS,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            logger.info("Playwright Chromium browser ready.")

    async def create_session(self, session_id: str, params: SessionCreate) -> ActiveBrowserSession:
        """Create an isolated browser context and instrument it with CDP listeners and screencasting."""
        await self.initialize()

        async with self._lock:
            if session_id in self._sessions:
                return self._sessions[session_id]

            if not self._browser:
                raise BrowserSessionError("Playwright browser instance is not running.")

            logger.info(f"Creating browser context for session: {session_id}")
            context = await self._browser.new_context(
                viewport={
                    "width": params.viewport_width or settings.PLAYWRIGHT_VIEWPORT_WIDTH,
                    "height": params.viewport_height or settings.PLAYWRIGHT_VIEWPORT_HEIGHT,
                },
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 DocuAgent/2.0",
            )

            page = await context.new_page()
            cdp_session = await context.new_cdp_session(page)

            # Instrument page scripts for DOM highlighting & in-page action capture
            highlight_color = params.highlight_color or settings.PLAYWRIGHT_HIGHLIGHT_COLOR
            injection_script = DOMHighlighter.get_injection_script(highlight_color)
            await page.add_init_script(injection_script)

            # Expose binding for action capture from page
            tracer = ActionTracer(session_id=session_id, page=page)

            async def _on_dom_action(action_data: dict):
                try:
                    await tracer.record_action(
                        action_type=action_data.get("action_type", "click"),
                        target_data=action_data.get("target"),
                        input_value=action_data.get("input_value"),
                    )
                except Exception as e:
                    logger.error(f"Error recording DOM action: {e}")

            await page.expose_binding("__docuagent_on_action", lambda source, val: asyncio.create_task(_on_dom_action(val)))

            # Screencasting & CDP Listeners
            screencaster = ScreencastStreamer(page=page, cdp_session=cdp_session)
            cdp_listener = CDPEventListener(page=page, cdp_session=cdp_session)
            await cdp_listener.initialize()

            # Handle page navigation trace
            cdp_listener.on_navigation(lambda url: asyncio.create_task(
                tracer.record_action(action_type="navigation", input_value=url)
            ))

            # Navigate to target URL
            try:
                await page.goto(params.target_url, wait_until="domcontentloaded", timeout=30000)
            except Exception as e:
                logger.warning(f"Initial navigation warning for {params.target_url}: {e}")

            # Start screencast stream
            await screencaster.start()

            active_session = ActiveBrowserSession(
                session_id=session_id,
                context=context,
                page=page,
                cdp_session=cdp_session,
                screencaster=screencaster,
                cdp_listener=cdp_listener,
                tracer=tracer,
                target_url=params.target_url,
                highlight_color=highlight_color,
            )

            self._sessions[session_id] = active_session
            logger.info(f"Session {session_id} successfully initialized and recording.")
            return active_session

    def get_session(self, session_id: str) -> Optional[ActiveBrowserSession]:
        """Retrieve an active session by ID."""
        return self._sessions.get(session_id)

    async def close_session(self, session_id: str):
        """Stop screencast, close context and remove session."""
        async with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                try:
                    await session.screencaster.stop()
                    await session.context.close()
                    logger.info(f"Closed browser session {session_id}.")
                except Exception as e:
                    logger.warning(f"Error closing session {session_id}: {e}")

    async def shutdown(self):
        """Cleanup all sessions and close Playwright."""
        for session_id in list(self._sessions.keys()):
            await self.close_session(session_id)
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Playwright Browser Manager shut down.")


_manager_instance: Optional[BrowserManager] = None


def get_browser_manager() -> BrowserManager:
    """Singleton getter for BrowserManager."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = BrowserManager()
    return _manager_instance
