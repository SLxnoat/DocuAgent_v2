"""WebSocket Endpoint for real-time Screencast streaming and interactive canvas input forwarding."""

import json
import base64
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websockets.connection_manager import manager
from app.engine.browser_manager import get_browser_manager
from app.core.config import settings
from app.core.logging import logger
from app.core.security import sanitize_identifier, SecurityValidationError, validate_target_url

router = APIRouter()


@router.websocket("/ws/screencast/{session_id}")
async def screencast_websocket_endpoint(websocket: WebSocket, session_id: str):
    """Bidirectional WebSocket for streaming screencast frames and transmitting full browser interactions."""
    try:
        session_id = sanitize_identifier(session_id, "session_id")
    except SecurityValidationError:
        await websocket.close(code=1008)
        return

    await manager.connect_screencast(session_id, websocket)
    browser_manager = get_browser_manager()
    session = browser_manager.get_session(session_id)

    # Callback to stream CDP frames
    async def _on_screencast_frame(data: str, metadata: dict):
        await manager.broadcast_screencast_frame(session_id, data, metadata)

    if session:
        session.screencaster.on_frame(_on_screencast_frame)
        # Send initial immediate snapshot so the canvas renders instantly
        try:
            screenshot_bytes = await session.page.screenshot(type="jpeg", quality=settings.SCREENCAST_QUALITY)
            b64_data = base64.b64encode(screenshot_bytes).decode("utf-8")
            await websocket.send_json({
                "type": "screencast_frame",
                "data": b64_data,
                "metadata": {
                    "offsetTop": 0,
                    "pageScaleFactor": 1,
                    "deviceWidth": settings.PLAYWRIGHT_VIEWPORT_WIDTH,
                    "deviceHeight": settings.PLAYWRIGHT_VIEWPORT_HEIGHT,
                    "url": session.page.url,
                    "title": await session.page.title(),
                },
            })
        except Exception as snap_err:
            logger.debug(f"Failed to capture initial screencast snapshot: {snap_err}")

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if not session:
                session = browser_manager.get_session(session_id)
                if session:
                    session.screencaster.on_frame(_on_screencast_frame)
                else:
                    continue

            if msg_type == "mouse":
                await session.screencaster.dispatch_mouse_event(
                    event_type=message.get("event"),
                    x=int(message.get("x", 0)),
                    y=int(message.get("y", 0)),
                    button=message.get("button", "left"),
                    click_count=int(message.get("clickCount", 1)),
                    delta_x=float(message.get("deltaX", 0.0)),
                    delta_y=float(message.get("deltaY", 0.0)),
                )
            elif msg_type == "keyboard":
                await session.screencaster.dispatch_keyboard_event(
                    event_type=message.get("event"),
                    key=message.get("key", ""),
                    text=message.get("text"),
                )
            elif msg_type == "navigate":
                url = message.get("url", "").strip()
                if url:
                    if not url.startswith("http://") and not url.startswith("https://"):
                        url = f"https://{url}"
                    try:
                        validated = validate_target_url(url)
                        await session.screencaster.navigate(validated)
                    except Exception as nav_err:
                        logger.warning(f"Interactive navigation error: {nav_err}")
            elif msg_type == "reload":
                await session.screencaster.reload()
            elif msg_type == "goBack":
                await session.screencaster.go_back()
            elif msg_type == "goForward":
                await session.screencaster.go_forward()

    except WebSocketDisconnect:
        if session:
            session.screencaster.remove_frame_callback(_on_screencast_frame)
        manager.disconnect_screencast(session_id, websocket)
    except Exception as e:
        logger.debug(f"Screencast WS loop closed: {e}")
        if session:
            session.screencaster.remove_frame_callback(_on_screencast_frame)
        manager.disconnect_screencast(session_id, websocket)

