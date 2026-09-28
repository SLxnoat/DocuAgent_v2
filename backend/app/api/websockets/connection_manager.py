"""WebSocket Connection and Room Manager."""

from typing import Dict, Set
from fastapi import WebSocket
from app.core.logging import logger


class ConnectionManager:
    """Manages active WebSocket channels grouped by session_id."""

    def __init__(self):
        # session_id -> Set[WebSocket]
        self._screencast_sockets: Dict[str, Set[WebSocket]] = {}
        self._event_sockets: Dict[str, Set[WebSocket]] = {}

    async def connect_screencast(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self._screencast_sockets:
            self._screencast_sockets[session_id] = set()
        self._screencast_sockets[session_id].add(websocket)
        logger.info(f"Connected screencast client to session: {session_id}")

    def disconnect_screencast(self, session_id: str, websocket: WebSocket):
        if session_id in self._screencast_sockets:
            self._screencast_sockets[session_id].discard(websocket)
            if not self._screencast_sockets[session_id]:
                del self._screencast_sockets[session_id]
        logger.info(f"Disconnected screencast client from session: {session_id}")

    async def broadcast_screencast_frame(self, session_id: str, frame_base64: str, metadata: dict):
        if session_id in self._screencast_sockets:
            payload = {
                "type": "screencast_frame",
                "data": frame_base64,
                "metadata": metadata,
            }
            for socket in list(self._screencast_sockets[session_id]):
                try:
                    await socket.send_json(payload)
                except Exception as e:
                    logger.debug(f"Failed to send frame to socket: {e}")

    async def connect_events(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self._event_sockets:
            self._event_sockets[session_id] = set()
        self._event_sockets[session_id].add(websocket)
        logger.info(f"Connected event listener to session: {session_id}")

    def disconnect_events(self, session_id: str, websocket: WebSocket):
        if session_id in self._event_sockets:
            self._event_sockets[session_id].discard(websocket)
            if not self._event_sockets[session_id]:
                del self._event_sockets[session_id]

    async def broadcast_event(self, session_id: str, event_type: str, data: dict):
        if session_id in self._event_sockets:
            payload = {
                "type": event_type,
                "data": data,
            }
            for socket in list(self._event_sockets[session_id]):
                try:
                    await socket.send_json(payload)
                except Exception as e:
                    logger.debug(f"Failed to send event: {e}")


manager = ConnectionManager()
