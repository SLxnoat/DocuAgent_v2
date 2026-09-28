"""WebSocket Endpoint for real-time Screencast streaming and interactive canvas input forwarding."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websockets.connection_manager import manager
from app.engine.browser_manager import get_browser_manager
from app.core.logging import logger

router = APIRouter()


@router.websocket("/ws/screencast/{session_id}")
async def screencast_websocket_endpoint(websocket: WebSocket, session_id: str):
    """Bidirectional WebSocket for receiving screencast frames and transmitting mouse/key events."""
    await manager.connect_screencast(session_id, websocket)
    browser_manager = get_browser_manager()
    session = browser_manager.get_session(session_id)

    if session:
        # Register frame callback to broadcast through manager
        session.screencaster.on_frame(
            lambda data, meta: manager.broadcast_screencast_frame(session_id, data, meta)
        )

    try:
        while True:
            # Receive input events from React frontend canvas
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if not session:
                session = browser_manager.get_session(session_id)
                if not session:
                    continue

            if msg_type == "mouse":
                await session.screencaster.dispatch_mouse_event(
                    event_type=message.get("event"),
                    x=int(message.get("x", 0)),
                    y=int(message.get("y", 0)),
                    button=message.get("button", "left"),
                    click_count=int(message.get("clickCount", 1)),
                )
            elif msg_type == "keyboard":
                await session.screencaster.dispatch_keyboard_event(
                    event_type=message.get("event"),
                    key=message.get("key", ""),
                    text=message.get("text"),
                )
    except WebSocketDisconnect:
        manager.disconnect_screencast(session_id, websocket)
    except Exception as e:
        logger.error(f"Error in screencast WS loop: {e}")
        manager.disconnect_screencast(session_id, websocket)
