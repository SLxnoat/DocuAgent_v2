"""Dynamic Supervisor / Orchestrator Node for intelligent multi-agent routing."""

import json
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import DocuAgentState
from app.agents.llm_factory import LLMFactory
from app.agents.prompts.supervisor import SUPERVISOR_SYSTEM_PROMPT
from app.core.logging import logger

MAX_SUPERVISOR_ITERATIONS = 5


async def supervisor_node(state: DocuAgentState) -> dict:
    """Evaluate state and dynamically select the next specialized agent to execute."""
    iteration = state.get("iteration_count", 0) + 1
    session_id = state.get("session_id", "unknown")
    logger.info(f"Dynamic Supervisor evaluating workflow state (Iteration #{iteration}) for session: {session_id}")

    # Safety guard against infinite loops
    if iteration > MAX_SUPERVISOR_ITERATIONS:
        logger.warning(f"Maximum supervisor iterations ({MAX_SUPERVISOR_ITERATIONS}) reached. Concluding pipeline.")
        return {
            "next_agent": "FINISH",
            "supervisor_directives": "Completed maximum allowed autonomous iterations.",
            "iteration_count": iteration,
        }

    # Extract state summary for supervisor LLM
    grouped_steps = state.get("grouped_steps") or []
    synthesized_steps = state.get("synthesized_steps") or []
    quality_report = state.get("quality_report")
    user_instruction = state.get("user_instruction")
    raw_traces = state.get("raw_action_traces") or []

    # Deterministic fast-path shortcuts for unambiguous states
    if user_instruction and not state.get("metadata", {}).get("refinement_handled"):
        logger.info("Supervisor detected active user refinement instruction. Routing to Chat Refiner.")
        return {
            "next_agent": "chat_refiner",
            "supervisor_directives": f"Apply user refinement instruction: {user_instruction}",
            "iteration_count": iteration,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "supervisor",
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision": "chat_refiner",
                    "reasoning": "Active user refinement prompt detected.",
                },
            ],
        }

    visual_assets = state.get("visual_assets")

    if not grouped_steps and raw_traces:
        logger.info("Supervisor detected unparsed raw traces. Routing to Intent Parser.")
        return {
            "next_agent": "intent_parser",
            "supervisor_directives": "Parse raw DOM interactions into logical semantic steps.",
            "iteration_count": iteration,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "supervisor",
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision": "intent_parser",
                    "reasoning": "Initial action traces require semantic grouping.",
                },
            ],
        }

    if grouped_steps and visual_assets is None:
        logger.info("Supervisor detected grouped steps without visual assets. Routing to Screenshot Agent.")
        return {
            "next_agent": "screenshot_agent",
            "supervisor_directives": "Annotate target element bounding boxes, draw callout badges, and generate focus crops.",
            "iteration_count": iteration,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "supervisor",
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision": "screenshot_agent",
                    "reasoning": "Grouped procedural steps require visual asset processing and callout annotation.",
                },
            ],
        }

    if grouped_steps and not synthesized_steps:
        logger.info("Supervisor detected grouped steps ready for synthesis. Routing to Technical Writer.")
        return {
            "next_agent": "technical_writer",
            "supervisor_directives": "Synthesize initial technical walkthrough manual from grouped procedural steps and visual callouts.",
            "iteration_count": iteration,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "supervisor",
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision": "technical_writer",
                    "reasoning": "Grouped steps and visual assets are ready for technical synthesis.",
                },
            ],
        }

    if synthesized_steps and not quality_report:
        logger.info("Supervisor detected newly synthesized manual. Routing to Quality Reviewer.")
        return {
            "next_agent": "quality_reviewer",
            "supervisor_directives": "Perform thorough quality assessment and critique on generated documentation.",
            "iteration_count": iteration,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "supervisor",
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision": "quality_reviewer",
                    "reasoning": "Synthesized documentation requires QA review.",
                },
            ],
        }

    # Complex / Revision State: LLM Supervisor Reasoning
    state_payload = {
        "iteration": iteration,
        "has_raw_traces": len(raw_traces) > 0,
        "grouped_steps_count": len(grouped_steps),
        "synthesized_steps_count": len(synthesized_steps),
        "quality_score": quality_report.get("score") if quality_report else None,
        "is_approved": quality_report.get("is_approved") if quality_report else False,
        "quality_suggestions": quality_report.get("suggestions", []) if quality_report else [],
        "quality_missing_items": quality_report.get("missing_items", []) if quality_report else [],
        "user_instruction": user_instruction,
    }

    llm = LLMFactory.get_chat_model(fast=True)
    messages = [
        SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
        HumanMessage(content=f"Current Multi-Agent State:\n{json.dumps(state_payload, indent=2)}"),
    ]

    try:
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()

        parsed = json.loads(content)
        next_agent = parsed.get("next_agent", "FINISH")
        directives = parsed.get("directives", "Proceed with execution.")
        reasoning = parsed.get("reasoning", "Autonomous decision by Supervisor Agent.")

        logger.info(f"Supervisor decided next agent: {next_agent} (Reason: {reasoning})")

        return {
            "next_agent": next_agent,
            "supervisor_directives": directives,
            "iteration_count": iteration,
            "agent_activity_log": [
                *state.get("agent_activity_log", []),
                {
                    "agent": "supervisor",
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision": next_agent,
                    "reasoning": reasoning,
                    "directives": directives,
                },
            ],
        }
    except Exception as e:
        logger.warning(f"Supervisor LLM reasoning encountered exception: {e}. Applying fallback rules.")
        if quality_report and quality_report.get("score", 0) >= 80:
            next_agent = "FINISH"
            directives = "Quality score is acceptable."
        elif synthesized_steps and not quality_report:
            next_agent = "quality_reviewer"
            directives = "Evaluate documentation."
        else:
            next_agent = "FINISH"
            directives = "Pipeline finalized."

        return {
            "next_agent": next_agent,
            "supervisor_directives": directives,
            "iteration_count": iteration,
        }
