"""Technical Writer Node — synthesizes structured guide and markdown output."""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import DocuAgentState
from app.agents.llm_factory import LLMFactory
from app.agents.prompts.technical_writer import TECHNICAL_WRITER_SYSTEM_PROMPT
from app.core.logging import logger


async def technical_writer_node(state: DocuAgentState) -> dict:
    """Generate professional step-by-step markdown manual from grouped steps."""
    logger.info(f"Executing Technical Writer Node for session: {state.get('session_id')}")
    grouped_steps = state.get("grouped_steps", [])
    workflow_intent = state.get("workflow_intent", "Application Workflow")
    target_url = state.get("target_url", "")

    llm = LLMFactory.get_chat_model(fast=False)
    user_payload = {
        "workflow_intent": workflow_intent,
        "target_url": target_url,
        "grouped_steps": grouped_steps,
    }

    messages = [
        SystemMessage(content=TECHNICAL_WRITER_SYSTEM_PROMPT),
        HumanMessage(content=f"Workflow Definition:\n{json.dumps(user_payload, indent=2)}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        parsed = json.loads(content)
        return {
            "synthesized_steps": parsed.get("synthesized_steps", []),
            "executive_summary": parsed.get("executive_summary", ""),
            "prerequisites": parsed.get("prerequisites", []),
            "raw_markdown": parsed.get("raw_markdown", ""),
        }
    except Exception as e:
        logger.error(f"Technical Writer node failed: {e}")
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
        }
