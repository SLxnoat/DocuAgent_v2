"""Prompt templates for DocuAgent multi-agent pipeline."""

from app.agents.prompts.supervisor import SUPERVISOR_SYSTEM_PROMPT
from app.agents.prompts.intent_parser import INTENT_PARSER_SYSTEM_PROMPT
from app.agents.prompts.technical_writer import TECHNICAL_WRITER_SYSTEM_PROMPT
from app.agents.prompts.quality_reviewer import QUALITY_REVIEWER_SYSTEM_PROMPT
from app.agents.prompts.chat_refiner import CHAT_REFINER_SYSTEM_PROMPT

__all__ = [
    "SUPERVISOR_SYSTEM_PROMPT",
    "INTENT_PARSER_SYSTEM_PROMPT",
    "TECHNICAL_WRITER_SYSTEM_PROMPT",
    "QUALITY_REVIEWER_SYSTEM_PROMPT",
    "CHAT_REFINER_SYSTEM_PROMPT",
]
