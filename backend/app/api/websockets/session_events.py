"""WebSocket Endpoint for real-time action trace logs and multi-agent pipeline progress."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websockets.connection_manager import manager
from app.engine.browser_manager import get_browser_manager
from app.core.logging import logger

router = APIRouter()


@router.websocket("/ws/events/{session_id}")
async def session_events_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket streaming action-trace notifications and agent pipeline progression."""
    await manager.connect_events(session_id, websocket)
    browser_manager = get_browser_manager()
    session = browser_manager.get_session(session_id)

    if session:
        # Hook action tracer callbacks to broadcast over websocket
        session.tracer.on_action_recorded(
            lambda trace: manager.broadcast_event(
                session_id,
                "action_recorded",
                trace.model_dump(mode="json"),
            )
        )

    try:
        while True:
            # Client can ping or send control frames
            msg = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect_events(session_id, websocket)
    except Exception as e:
        logger.debug(f"Event WS closed: {e}")
        manager.disconnect_events(session_id, websocket)
