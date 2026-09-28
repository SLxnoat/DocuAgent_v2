"""Human-in-the-Loop Chat Refinement Endpoints."""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRefineRequest, ChatRefineResponse
from app.api.v1.endpoints.documents import _documents_db
from app.agents.nodes.chat_refiner import chat_refiner_node
from app.agents.state import DocuAgentState
from app.core.logging import logger

router = APIRouter()


@router.post("/refine", response_model=ChatRefineResponse)
async def refine_document_section(payload: ChatRefineRequest):
    """Refine or modify specific document sections based on user feedback using Chat Refiner Agent."""
    if payload.document_id not in _documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = _documents_db[payload.document_id]

    state_input: DocuAgentState = {
        "session_id": doc.session_id,
        "target_url": "",
        "raw_action_traces": [],
        "workflow_intent": doc.title,
        "grouped_steps": None,
        "synthesized_steps": [s.model_dump() if hasattr(s, "model_dump") else s for s in doc.steps],
        "executive_summary": doc.executive_summary,
        "prerequisites": doc.prerequisites,
        "raw_markdown": doc.raw_markdown,
        "quality_report": doc.quality_report.model_dump() if doc.quality_report else None,
        "review_iteration": 0,
        "is_approved": True,
        "user_instruction": payload.prompt,
        "target_step_number": payload.target_step_number,
        "refinement_history": [m.model_dump(mode="json") for m in payload.history],
        "error_message": None,
        "metadata": {},
    }

    try:
        updated_state = await chat_refiner_node(state_input)
        reply = updated_state.get("metadata", {}).get("last_refinement_reply", "Applied changes successfully.")
        modified_steps = updated_state.get("metadata", {}).get("modified_steps", [])
        
        # Update in-memory document
        doc.steps = updated_state.get("synthesized_steps", doc.steps)
        doc.raw_markdown = updated_state.get("raw_markdown", doc.raw_markdown)
        doc.version += 1
        doc.updated_at = datetime.utcnow()

        return ChatRefineResponse(
            document_id=doc.id,
            reply_message=reply,
            updated_steps=doc.steps,
            updated_markdown=doc.raw_markdown,
            modified_step_numbers=modified_steps,
        )
    except Exception as e:
        logger.error(f"Chat refinement error: {e}")
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")
