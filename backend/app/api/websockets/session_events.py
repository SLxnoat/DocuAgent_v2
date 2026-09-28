"""WebSocket Endpoint for real-time action trace logs and multi-agent pipeline progress."""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.api.websockets.connection_manager import manager
from app.engine.browser_manager import get_browser_manager
from app.core.logging import logger
from app.core.security import sanitize_identifier, SecurityValidationError

router = APIRouter()


@router.websocket("/ws/events/{session_id}")
async def session_events_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket streaming action-trace notifications and agent pipeline progression."""
    try:
        session_id = sanitize_identifier(session_id, "session_id")
    except SecurityValidationError:
        await websocket.close(code=1008)
        return

    await manager.connect_events(session_id, websocket)
    browser_manager = get_browser_manager()
    session = browser_manager.get_session(session_id)

    async def _on_trace_captured(trace):
        await manager.broadcast_event(
            session_id,
            "action_recorded",
            trace.model_dump(mode="json"),
        )

    if session:
        session.tracer.on_action_recorded(_on_trace_captured)

    try:
        while True:
            msg = await websocket.receive_text()
            if not session:
                session = browser_manager.get_session(session_id)
                if session:
                    session.tracer.on_action_recorded(_on_trace_captured)
    except WebSocketDisconnect:
        if session:
            session.tracer.remove_action_callback(_on_trace_captured)
        manager.disconnect_events(session_id, websocket)
    except Exception as e:
        logger.debug(f"Event WS closed: {e}")
        if session:
            session.tracer.remove_action_callback(_on_trace_captured)
        manager.disconnect_events(session_id, websocket)

