"""Technical Writer Node — synthesizes structured guide and markdown output with dynamic directives."""

import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import DocuAgentState
from app.agents.llm_factory import LLMFactory
from app.agents.prompts.technical_writer import TECHNICAL_WRITER_SYSTEM_PROMPT
from app.core.logging import logger


async def technical_writer_node(state: DocuAgentState) -> dict:
    """Generate professional step-by-step markdown manual from grouped steps guided by supervisor directives."""
    session_id = state.get("session_id", "unknown")
    directives = state.get("supervisor_directives", "Generate comprehensive technical walkthrough.")
    logger.info(f"Executing Technical Writer Node for session {session_id} with directives: '{directives}'")

    grouped_steps = state.get("grouped_steps", [])
    workflow_intent = state.get("workflow_intent", "Application Workflow")
    target_url = state.get("target_url", "")
    existing_markdown = state.get("raw_markdown")

    llm = LLMFactory.get_chat_model(fast=False)
    user_payload = {
        "workflow_intent": workflow_intent,
        "target_url": target_url,
        "grouped_steps": grouped_steps,
        "supervisor_directives": directives,
        "existing_draft": existing_markdown,
    }

    messages = [
        SystemMessage(content=TECHNICAL_WRITER_SYSTEM_PROMPT),
        HumanMessage(content=f"Workflow Synthesis Request with Directives:\n{json.dumps(user_payload, indent=2)}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        parsed = json.loads(content)
        synth_steps = parsed.get("synthesized_steps", [])
        raw_md = parsed.get("raw_markdown", "")
        visual_assets = state.get("visual_assets") or []

        # Merge visual assets (annotated screenshots & focus crops) into synthesized steps
        asset_map = {a["step_number"]: a for a in visual_assets if "step_number" in a}
        for idx, s in enumerate(synth_steps, 1):
            step_num = s.get("step_number", idx)
            asset = asset_map.get(step_num) or (visual_assets[idx - 1] if idx - 1 < len(visual_assets) else None)
            if asset:
                s["screenshot_url"] = asset.get("annotated_screenshot_url") or asset.get("raw_screenshot_url")
                s["annotated_screenshot_url"] = asset.get("annotated_screenshot_url")
                if asset.get("focus_crop_url"):
                    s["focus_crop_url"] = asset["focus_crop_url"]

        return {
            "synthesized_steps": synth_steps,
            "executive_summary": parsed.get("executive_summary", ""),
            "prerequisites": parsed.get("prerequisites", []),
            "raw_markdown": raw_md,
            "quality_report": None,  # Reset quality report so next evaluation is fresh
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "technical_writer",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success",
                    "steps_generated": len(synth_steps),
                    "applied_directives": directives,
                },
            ],
        }
    except Exception as e:
        logger.error(f"Technical Writer node error: {e}")
        # Build baseline markdown fallback
        md_lines = [
            f"# {workflow_intent}",
            "",
            "## Executive Summary",
            f"This guide documents the procedures for interacting with {target_url}.",
            "",
            "## Steps",
            "",
        ]
        synth_steps = []
        for s in grouped_steps:
            step_num = s.get("step_number", 1)
            title = s.get("title", "Action Step")
            instr = f"Navigate and execute {s.get('primary_action', 'action')} on {s.get('target_element_desc', 'element')}."
            md_lines.append(f"### Step {step_num}: {title}")
            md_lines.append(f"{instr}\n")
            synth_steps.append({
                "step_number": step_num,
                "title": title,
                "instruction": instr,
                "detailed_description": s.get("goal", ""),
                "target_ui_element": s.get("target_element_desc"),
                "screenshot_url": s.get("screenshot_path"),
                "callouts": [],
            })

        return {
            "synthesized_steps": synth_steps,
            "executive_summary": f"Documentation for {workflow_intent}",
            "prerequisites": ["Valid user account", "Access to the web application"],
            "raw_markdown": "\n".join(md_lines),
            "quality_report": None,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "technical_writer",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "fallback",
                    "steps_generated": len(synth_steps),
                },
            ],
        }
