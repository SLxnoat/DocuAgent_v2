"""Chat Refiner Node — applies targeted HITL human edits to specific sections."""

import json
from langchain_core.messages import SystemMessage, HumanMessage
from app.agents.state import DocuAgentState
from app.agents.llm_factory import LLMFactory
from app.agents.prompts.chat_refiner import CHAT_REFINER_SYSTEM_PROMPT
from app.core.logging import logger


async def chat_refiner_node(state: DocuAgentState) -> dict:
    """Perform granular updates to the documentation based on natural language user feedback."""
    logger.info("Executing Chat Refiner Node")
    user_instruction = state.get("user_instruction", "")
    target_step_number = state.get("target_step_number")
    current_steps = state.get("synthesized_steps", [])
    current_markdown = state.get("raw_markdown", "")

    payload = {
        "instruction": user_instruction,
        "target_step_number": target_step_number,
        "current_steps": current_steps,
        "current_markdown": current_markdown,
    }

    llm = LLMFactory.get_chat_model(fast=False)
    messages = [
        SystemMessage(content=CHAT_REFINER_SYSTEM_PROMPT),
        HumanMessage(content=f"Refinement Request:\n{json.dumps(payload, indent=2)}"),
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
            "synthesized_steps": parsed.get("updated_steps", current_steps),
            "raw_markdown": parsed.get("updated_markdown", current_markdown),
            "metadata": {
                **state.get("metadata", {}),
                "last_refinement_reply": parsed.get("reply_message", "Updated documentation based on feedback."),
                "modified_steps": parsed.get("modified_step_numbers", []),
            },
        }
    except Exception as e:
        logger.error(f"Chat Refiner error: {e}")
        return {
            "metadata": {
                **state.get("metadata", {}),
                "last_refinement_reply": f"Could not apply refinement automatically: {str(e)}",
            }
        }
