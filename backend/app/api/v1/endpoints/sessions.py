"""Recording Session Management Endpoints."""

import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.session import SessionCreate, SessionResponse, SessionStatus
from app.schemas.action_trace import ActionTrace
from app.engine.browser_manager import get_browser_manager
from app.agents.graph import get_compiled_graph
from app.agents.state import DocuAgentState
from app.core.logging import logger
from app.core.security import validate_target_url, sanitize_identifier, SecurityValidationError

router = APIRouter()

# In-memory session store (with DB sync)
_sessions_db: dict[str, SessionResponse] = {}
_action_store: dict[str, list[ActionTrace]] = {}


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_and_start_session(payload: SessionCreate):
    """Initialize a new browser recording session and open target URL."""
    try:
        validated_url = validate_target_url(payload.target_url)
        payload.target_url = validated_url
    except SecurityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    browser_manager = get_browser_manager()

    try:
        active_sess = await browser_manager.create_session(session_id, payload)
        
        session_obj = SessionResponse(
            id=session_id,
            target_url=payload.target_url,
            title=payload.title or "Untitled Workflow",
            description=payload.description,
            status=SessionStatus.RECORDING,
            action_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            active_url=payload.target_url,
            metadata={"viewport": f"{payload.viewport_width}x{payload.viewport_height}"},
        )
        _sessions_db[session_id] = session_obj
        _action_store[session_id] = []
        return session_obj
    except Exception as e:
        logger.error(f"Failed to start recording session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start browser session: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session_status(session_id: str):
    """Fetch status and current statistics of a recording session."""
    try:
        session_id = sanitize_identifier(session_id, "session_id")
    except SecurityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if session_id not in _sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    browser_manager = get_browser_manager()
    active_sess = browser_manager.get_session(session_id)
    session_obj = _sessions_db[session_id]
    
    if active_sess:
        session_obj.action_count = len(active_sess.tracer.get_all_traces())
        session_obj.active_url = active_sess.page.url
        session_obj.updated_at = datetime.utcnow()

    return session_obj


@router.get("/{session_id}/actions", response_model=List[ActionTrace])
async def get_session_actions(session_id: str):
    """Retrieve all recorded DOM actions for a session."""
    browser_manager = get_browser_manager()
    active_sess = browser_manager.get_session(session_id)
    if active_sess:
        return active_sess.tracer.get_all_traces()
    return _action_store.get(session_id, [])


@router.post("/{session_id}/stop", response_model=SessionResponse)
async def stop_session_and_finalize(session_id: str):
    """Stop active recording session and prepare traces for multi-agent synthesis."""
    if session_id not in _sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")

    browser_manager = get_browser_manager()
    active_sess = browser_manager.get_session(session_id)

    if active_sess:
        _action_store[session_id] = active_sess.tracer.get_all_traces()
        await browser_manager.close_session(session_id)

    session_obj = _sessions_db[session_id]
    session_obj.status = SessionStatus.COMPLETED
    session_obj.action_count = len(_action_store.get(session_id, []))
    session_obj.updated_at = datetime.utcnow()

    return session_obj
