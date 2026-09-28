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
from app.core.security import sanitize_identifier, SecurityValidationError

router = APIRouter()

# In-memory document storage
_documents_db: dict[str, DocumentSchema] = {}


@router.post("/generate/{session_id}", response_model=DocumentSchema)
async def generate_document_from_session(session_id: str):
    """Execute LangGraph multi-agent pipeline to generate comprehensive documentation from recorded actions."""
    try:
        session_id = sanitize_identifier(session_id, "session_id")
    except SecurityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        "next_agent": None,
        "supervisor_directives": None,
        "iteration_count": 0,
        "agent_activity_log": [],
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
    steps = final_state.get("synthesized_steps") or []
    raw_md = final_state.get("raw_markdown")

    # Resilience guarantee: If LLM failed or returned empty steps, generate clean walkthrough from action traces
    if not steps and actions:
        for idx, a in enumerate(actions, 1):
            elem = a.target_element
            target_desc = elem.inner_text if elem and elem.inner_text else (elem.css_selector if elem else (a.input_value or "element"))
            steps.append({
                "step_number": idx,
                "title": f"{a.action_type.value.capitalize()} {target_desc}",
                "instruction": f"Navigate to {a.page_title or 'page'} and execute {a.action_type.value} on {target_desc}.",
                "detailed_description": f"User interaction recorded at {a.page_url}.",
                "target_ui_element": target_desc,
                "screenshot_url": a.screenshot_url,
                "callouts": [],
            })

    if not raw_md or raw_md.strip() in ("# Generated Documentation", ""):
        lines = [
            f"# {session.title}",
            "",
            f"**Target URL:** `{session.target_url}`",
            "",
            "## Executive Summary",
            f"This manual details the step-by-step procedures for the workflow at {session.target_url}.",
            "",
            "## Procedure Steps",
            "",
        ]
        for s in steps:
            num = s.get("step_number", 1)
            title = s.get("title", "Step")
            instr = s.get("instruction", "")
            img_url = s.get("screenshot_url")
            lines.append(f"### Step {num}: {title}")
            lines.append(f"{instr}\n")
            if img_url:
                lines.append(f"![Step {num}]({img_url})\n")
        raw_md = "\n".join(lines)

    doc = DocumentSchema(
        id=doc_id,
        session_id=session_id,
        title=final_state.get("workflow_intent") or session.title,
        executive_summary=final_state.get("executive_summary") or f"Documentation for workflow at {session.target_url}",
        prerequisites=final_state.get("prerequisites") or ["Access to target web application"],
        steps=steps,
        troubleshooting=[],
        raw_markdown=raw_md,
        quality_report=final_state.get("quality_report"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=1,
    )

    _documents_db[doc_id] = doc
    logger.info(f"Successfully synthesized document {doc_id} with {len(steps)} steps.")
    return doc


@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(document_id: str):
    """Retrieve generated document by ID."""
    try:
        document_id = sanitize_identifier(document_id, "document_id")
    except SecurityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if document_id not in _documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return _documents_db[document_id]


@router.post("/export")
async def export_document(payload: ExportRequest):
    """Export document as high-resolution PDF or styled HTML."""
    try:
        doc_id = sanitize_identifier(payload.document_id, "document_id")
        payload.document_id = doc_id
    except SecurityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

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


@router.get("/{document_id}/download")
async def download_document_file(document_id: str, format: ExportFormat = ExportFormat.PDF):
    """Direct file download endpoint for compiled PDF or HTML manuals."""
    try:
        document_id = sanitize_identifier(document_id, "document_id")
    except SecurityValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if document_id not in _documents_db:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = _documents_db[document_id]
    if format == ExportFormat.PDF:
        pdf_path = settings.EXPORTS_DIR / f"{doc.id}.pdf"
        if not pdf_path.exists():
            generator = PDFGenerator()
            generator.generate_pdf(document=doc, output_path=pdf_path)

        return FileResponse(
            path=str(pdf_path),
            filename=f"{doc.title.replace(' ', '_')}.pdf",
            media_type="application/pdf",
        )
    elif format == ExportFormat.HTML:
        renderer = HTMLRenderer()
        html = renderer.render_manual_html(document=doc)
        return HTMLResponse(content=html)
    elif format == ExportFormat.MARKDOWN:
        return {"markdown": doc.raw_markdown}

    return {"document": doc.model_dump(mode="json")}

