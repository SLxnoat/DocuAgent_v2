"""Abstract Base Class for Multi-Agent Orchestration Pipelines in DocuAgent AI."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseAgentPipeline(ABC):
    """Abstract interface for multi-agent documentation generation and refinement engines."""

    @abstractmethod
    async def generate_document(
        self,
        session_id: str,
        target_url: str,
        raw_action_traces: List[Dict[str, Any]],
        workflow_intent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synthesize a complete procedural technical guide from raw action traces and telemetry.

        Args:
            session_id: Unique recording session identifier.
            target_url: Base URL of the recorded application workflow.
            raw_action_traces: List of raw CDP telemetry action dictionaries.
            workflow_intent: Optional initial goal or title provided by the user.

        Returns:
            Dictionary with generated document state matching DocumentSchema fields:
            - title: str
            - executive_summary: str
            - prerequisites: list[str]
            - steps: list[dict]
            - raw_markdown: str
            - quality_report: dict | None
            - metadata: dict
        """
        pass

    @abstractmethod
    async def refine_document(
        self,
        document_dict: Dict[str, Any],
        user_instruction: str,
        target_step_number: Optional[int] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Apply targeted Human-in-the-Loop natural language edits to an existing document.

        Args:
            document_dict: Current document state dictionary.
            user_instruction: Natural language instruction/feedback from the user.
            target_step_number: Optional 1-indexed target step number to focus revisions on.
            history: Optional conversation message history.

        Returns:
            Dictionary containing:
            - reply_message: str
            - updated_steps: list[dict]
            - updated_markdown: str
            - modified_step_numbers: list[int]
            - quality_report: dict | None
        """
        pass
