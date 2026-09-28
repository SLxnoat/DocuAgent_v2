"""Document Generation, Retrieval, and Export Endpoints."""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from app.schemas.document import DocumentSchema, ExportRequest, ExportFormat
from app.schemas.session import SessionStatus
from app.api.v1.endpoints.sessions import _sessions_db, _action_store
from app.agents.graph import get_compiled_graph
from app.agents.state import DocuAgentState
from app.exporter.pdf_generator import PDFGenerator
from app.exporter.html_renderer import HTMLRenderer
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()

# In-memory document storage
_documents_db: dict[str, DocumentSchema] = {}


@router.post("/generate/{session_id}", response_model=DocumentSchema)
async def generate_document_from_session(session_id: str):
    """Execute LangGraph multi-agent pipeline to generate comprehensive documentation from recorded actions."""
    if session_id not in _sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")

    session = _sessions_db[session_id]
    actions = _action_store.get(session_id, [])

    if not actions:
        logger.warning(f"No actions recorded for session {session_id}. Proceeding with minimal workflow context.")

    raw_traces_dicts = [a.model_dump(mode="json") for a in actions]

    initial_state: DocuAgentState = {
        "session_id": session_id,
        "target_url": session.target_url,
        "raw_action_traces": raw_traces_dicts,
        "workflow_intent": session.title,
        "grouped_steps": None,
        "synthesized_steps": None,
        "executive_summary": None,
        "prerequisites": None,
        "raw_markdown": None,
        "quality_report": None,
        "review_iteration": 0,
        "is_approved": False,
        "user_instruction": None,
        "target_step_number": None,
        "refinement_history": [],
        "error_message": None,
        "metadata": {},
    }

    graph = get_compiled_graph()
    try:
        final_state = await graph.ainvoke(initial_state)
    except Exception as e:
        logger.error(f"LangGraph execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-Agent execution failed: {str(e)}")

    doc_id = f"doc_{uuid.uuid4().hex[:10]}"
    doc = DocumentSchema(
        id=doc_id,
        session_id=session_id,
        title=final_state.get("workflow_intent") or session.title,
        executive_summary=final_state.get("executive_summary") or f"Documentation for workflow at {session.target_url}",
        prerequisites=final_state.get("prerequisites") or ["Access to target web application"],
        steps=final_state.get("synthesized_steps") or [],
        troubleshooting=[],
        raw_markdown=final_state.get("raw_markdown") or "# Generated Documentation",
        quality_report=final_state.get("quality_report"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=1,
    )

    _documents_db[doc_id] = doc
    logger.info(f"Successfully synthesized document {doc_id} with score {doc.quality_report.score if doc.quality_report else 'N/A'}")
    return doc


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(document_id: str):
    """Retrieve generated document by ID."""
    if document_id not in _documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return _documents_db[document_id]


@router.post("/export")
async def export_document(payload: ExportRequest):
    """Export document as high-resolution PDF or styled HTML."""
    if payload.document_id not in _documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = _documents_db[payload.document_id]

    if payload.format == ExportFormat.PDF:
        generator = PDFGenerator()
        pdf_path = settings.EXPORTS_DIR / f"{doc.id}.pdf"
        try:
            generator.generate_pdf(
                document=doc,
                output_path=pdf_path,
                target_url=doc.session_id,
                include_screenshots=payload.include_screenshots,
            )
            return FileResponse(
                path=str(pdf_path),
                filename=f"{doc.title.replace(' ', '_')}.pdf",
                media_type="application/pdf",
            )
        except Exception as e:
            logger.error(f"PDF export error: {e}")
            raise HTTPException(status_code=500, detail=f"PDF Export error: {str(e)}")

    elif payload.format == ExportFormat.HTML:
        renderer = HTMLRenderer()
        html = renderer.render_manual_html(document=doc, include_screenshots=payload.include_screenshots)
        return HTMLResponse(content=html)

    elif payload.format == ExportFormat.MARKDOWN:
        return {"markdown": doc.raw_markdown}

    return {"document": doc.model_dump(mode="json")}
