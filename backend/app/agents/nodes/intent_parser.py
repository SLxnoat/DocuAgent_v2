"""Intent Parser Node — transforms raw action traces into grouped goals."""

import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import DocuAgentState
from app.agents.llm_factory import LLMFactory
from app.agents.prompts.intent_parser import INTENT_PARSER_SYSTEM_PROMPT
from app.core.logging import logger


async def intent_parser_node(state: DocuAgentState) -> dict:
    """Analyze raw action traces and structure them into grouped procedural steps."""
    session_id = state.get("session_id", "unknown")
    directives = state.get("supervisor_directives", "Group raw actions into logical steps.")
    logger.info(f"Executing Intent Parser Node for session {session_id} with directives: '{directives}'")

    traces = state.get("raw_action_traces", [])
    
    if not traces:
        logger.warning("No action traces found to parse.")
        return {
            "workflow_intent": "General Navigation Workflow",
            "grouped_steps": [],
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "intent_parser",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "empty_traces",
                    "steps_grouped": 0,
                },
            ],
        }

    # Format simplified trace summary for LLM context
    trace_payload = []
    for t in traces:
        target = t.get("target_element") or {}
        trace_payload.append({
            "id": t.get("id"),
            "action_type": t.get("action_type"),
            "page_title": t.get("page_title"),
            "page_url": t.get("page_url"),
            "selector": target.get("css_selector"),
            "inner_text": target.get("inner_text"),
            "input_value": t.get("input_value"),
            "screenshot_url": t.get("screenshot_url"),
        })

    llm = LLMFactory.get_chat_model(fast=False)
    user_content = {
        "target_url": state.get("target_url"),
        "supervisor_directives": directives,
        "action_traces": trace_payload,
    }

    messages = [
        SystemMessage(content=INTENT_PARSER_SYSTEM_PROMPT),
        HumanMessage(content=f"Intent Parsing Request:\n{json.dumps(user_content, indent=2)}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        parsed = json.loads(content)
        intent = parsed.get("workflow_intent", "Automated User Workflow")
        grouped = parsed.get("grouped_steps", [])

        return {
            "workflow_intent": intent,
            "grouped_steps": grouped,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "intent_parser",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success",
                    "intent": intent,
                    "steps_grouped": len(grouped),
                },
            ],
        }
    except Exception as e:
        logger.error(f"Intent Parser failed with exception: {e}")
        # Fallback to direct mapping if LLM JSON decoding encounters issue
        fallback_steps = []
        for idx, t in enumerate(traces, 1):
            fallback_steps.append({
                "step_number": idx,
                "title": f"Perform {t.get('action_type', 'Action')}",
                "goal": f"Interact with UI element on {t.get('page_title', 'page')}",
                "raw_action_ids": [t.get("id")],
                "primary_action": t.get("action_type"),
                "target_element_desc": (t.get("target_element") or {}).get("inner_text") or "UI Element",
                "input_value": t.get("input_value"),
                "screenshot_path": t.get("screenshot_url"),
            })
        return {
            "workflow_intent": "User Recorded Workflow",
            "grouped_steps": fallback_steps,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "intent_parser",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "fallback",
                    "steps_grouped": len(fallback_steps),
                },
            ],
        }
