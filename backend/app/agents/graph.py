"""LangGraph StateGraph construction and compilation for DocuAgent."""

from langgraph.graph import StateGraph, START, END
from app.agents.state import DocuAgentState
from app.agents.nodes.intent_parser import intent_parser_node
from app.agents.nodes.technical_writer import technical_writer_node
from app.agents.nodes.quality_reviewer import quality_reviewer_node
from app.agents.nodes.chat_refiner import chat_refiner_node
from app.core.logging import logger


def should_continue_review(state: DocuAgentState) -> str:
    """Conditional router for quality review loop."""
    is_approved = state.get("is_approved", True)
    iteration = state.get("review_iteration", 0)
    
    # If not approved and under max attempts (1 auto-remediation attempt), cycle back
    if not is_approved and iteration < 2:
        logger.info("Quality review requested revision. Routing back to Technical Writer.")
        return "technical_writer"
    return END


def create_documentation_graph() -> StateGraph:
    """Build and compile the multi-agent LangGraph workflow."""
    workflow = StateGraph(DocuAgentState)

    # Register Nodes
    workflow.add_node("intent_parser", intent_parser_node)
    workflow.add_node("technical_writer", technical_writer_node)
    workflow.add_node("quality_reviewer", quality_reviewer_node)
    workflow.add_node("chat_refiner", chat_refiner_node)

    # Pipeline Flow
    workflow.add_edge(START, "intent_parser")
    workflow.add_edge("intent_parser", "technical_writer")
    workflow.add_edge("technical_writer", "quality_reviewer")
    
    # Conditional edge from Quality Reviewer
    workflow.add_conditional_edges(
        "quality_reviewer",
        should_continue_review,
        {
            "technical_writer": "technical_writer",
            END: END,
        },
    )

    # Refiner node loop
    workflow.add_edge("chat_refiner", "quality_reviewer")

    return workflow


_compiled_graph = None


def get_compiled_graph():
    """Retrieve compiled LangGraph singleton instance."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = create_documentation_graph()
        _compiled_graph = graph.compile()
        logger.info("Compiled LangGraph documentation pipeline.")
    return _compiled_graph
