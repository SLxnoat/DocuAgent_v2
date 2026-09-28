"""LangGraph Dynamic Multi-Agent StateGraph with Autonomous Supervisor Orchestration."""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from app.agents.state import DocuAgentState
from app.agents.nodes.supervisor import supervisor_node
from app.agents.nodes.intent_parser import intent_parser_node
from app.agents.nodes.screenshot_agent import screenshot_agent_node
from app.agents.nodes.technical_writer import technical_writer_node
from app.agents.nodes.quality_reviewer import quality_reviewer_node
from app.agents.nodes.chat_refiner import chat_refiner_node
from app.core.logging import logger


def route_supervisor_decision(state: DocuAgentState) -> str:
    """Dynamic router mapping the Supervisor Agent's decision to the next node or termination."""
    next_agent = state.get("next_agent", "FINISH")
    logger.info(f"Dynamic Agent Router dispatched target: [{next_agent}]")

    if next_agent == "intent_parser":
        return "intent_parser"
    elif next_agent == "screenshot_agent":
        return "screenshot_agent"
    elif next_agent == "technical_writer":
        return "technical_writer"
    elif next_agent == "quality_reviewer":
        return "quality_reviewer"
    elif next_agent == "chat_refiner":
        return "chat_refiner"
    
    return END


def create_documentation_graph() -> StateGraph:
    """Build and compile the dynamic multi-agent LangGraph network."""
    workflow = StateGraph(DocuAgentState)

    # Register Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("intent_parser", intent_parser_node)
    workflow.add_node("screenshot_agent", screenshot_agent_node)
    workflow.add_node("technical_writer", technical_writer_node)
    workflow.add_node("quality_reviewer", quality_reviewer_node)
    workflow.add_node("chat_refiner", chat_refiner_node)

    # 1. Flow starts at the Dynamic Supervisor
    workflow.add_edge(START, "supervisor")

    # 2. Dynamic conditional dispatch from Supervisor to chosen agent or END
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor_decision,
        {
            "intent_parser": "intent_parser",
            "screenshot_agent": "screenshot_agent",
            "technical_writer": "technical_writer",
            "quality_reviewer": "quality_reviewer",
            "chat_refiner": "chat_refiner",
            END: END,
        },
    )

    # 3. All agents report back to Supervisor for dynamic evaluation of next step
    workflow.add_edge("intent_parser", "supervisor")
    workflow.add_edge("screenshot_agent", "supervisor")
    workflow.add_edge("technical_writer", "supervisor")
    workflow.add_edge("quality_reviewer", "supervisor")
    workflow.add_edge("chat_refiner", "supervisor")

    return workflow


_compiled_graph = None


def get_compiled_graph():
    """Retrieve compiled dynamic LangGraph singleton instance."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = create_documentation_graph()
        _compiled_graph = graph.compile()
        logger.info("Compiled Dynamic Multi-Agent LangGraph Network.")
    return _compiled_graph
