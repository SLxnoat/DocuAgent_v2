"""Celery tasks for executing the multi-agent LangGraph workflow asynchronously."""

import asyncio
from app.workers.celery_app import celery
from app.agents.graph import get_compiled_graph
from app.agents.state import DocuAgentState
from app.core.logging import logger


@celery.task(bind=True, name="tasks.run_agent_pipeline")
def run_agent_pipeline_task(self, session_id: str, target_url: str, raw_action_traces: list):
    """Run LangGraph pipeline to synthesize user guide asynchronously."""
    logger.info(f"Starting Celery Agent Pipeline Task for session: {session_id}")
    graph = get_compiled_graph()

    initial_state: DocuAgentState = {
        "session_id": session_id,
        "target_url": target_url,
        "raw_action_traces": raw_action_traces,
        "next_agent": None,
        "supervisor_directives": None,
        "iteration_count": 0,
        "agent_activity_log": [],
        "workflow_intent": None,
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

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    final_state = loop.run_until_complete(graph.ainvoke(initial_state))
    logger.info(f"Completed Celery Agent Pipeline Task for session: {session_id}")
    
    return {
        "session_id": session_id,
        "executive_summary": final_state.get("executive_summary"),
        "steps": final_state.get("synthesized_steps"),
        "raw_markdown": final_state.get("raw_markdown"),
        "quality_report": final_state.get("quality_report"),
    }
