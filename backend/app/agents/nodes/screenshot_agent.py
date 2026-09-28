"""Screenshot Agent Node — processes, annotates, crops, and optimizes visual assets for SOP manuals."""

from datetime import datetime
from typing import Dict, Any, List
from app.agents.state import DocuAgentState
from app.engine.image_annotator import ImageAnnotator
from app.core.config import settings
from app.core.logging import logger


async def screenshot_agent_node(state: DocuAgentState) -> dict:
    """Analyze step interaction targets and generate numbered callouts, neon outlines, and focus crops."""
    session_id = state.get("session_id", "unknown")
    directives = state.get("supervisor_directives", "Process and annotate visual assets.")
    logger.info(f"Executing Screenshot Agent for session {session_id} with directives: '{directives}'")

    grouped_steps = state.get("grouped_steps") or []
    raw_traces = state.get("raw_action_traces") or []
    highlight_color = state.get("metadata", {}).get("highlight_color") or settings.PLAYWRIGHT_HIGHLIGHT_COLOR

    annotator = ImageAnnotator(session_id=session_id)
    visual_assets: List[Dict[str, Any]] = []
    updated_steps = []

    for idx, step in enumerate(grouped_steps, 1):
        step_dict = dict(step)
        asset = annotator.process_step_image(
            step_number=idx,
            step_data=step_dict,
            raw_traces=raw_traces,
            highlight_color=highlight_color,
        )

        if asset:
            visual_assets.append(asset)
            # Enrich step with annotated image paths and focus crop thumbnail.
            # Note: screenshot_url is intentionally NOT overwritten here — the
            # technical_writer merges annotated_screenshot_url → screenshot_url
            # during its visual asset pass, preserving the original raw URL.
            step_dict["annotated_screenshot_url"] = asset["annotated_screenshot_url"]
            if asset.get("focus_crop_url"):
                step_dict["focus_crop_url"] = asset["focus_crop_url"]
            step_dict["has_pii_redaction"] = asset.get("has_pii_redaction", False)

        updated_steps.append(step_dict)

    logger.info(f"Screenshot Agent completed: {len(visual_assets)} visual assets generated and annotated.")

    return {
        "visual_assets": visual_assets,
        "grouped_steps": updated_steps,
        "visual_processing_status": "completed",
        "agent_activity_log": [
            *state.get("agent_activity_log", []),
            {
                "agent": "screenshot_agent",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "success",
                "assets_processed": len(visual_assets),
                "directives": directives,
            },
        ],
    }
