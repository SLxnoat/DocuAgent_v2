"""LLM Factory for configuring and instantiating model backends."""

from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.core.logging import logger


class LLMFactory:
    """Factory creating LLM instances based on configured providers."""

    @classmethod
    def get_chat_model(
        cls,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        fast: bool = False,
    ) -> BaseChatModel:
        """Instantiate a ChatModel instance."""
        target_model = model_name or (settings.FAST_MODEL if fast else settings.DEFAULT_MODEL)
        provider = settings.LLM_PROVIDER.lower()

        logger.info(f"Initializing LLM Provider: {provider} with Model: {target_model}")

        if provider in ("ollama_cloud", "ollama_local", "ollama"):
            # Ensure base_url points to an actual Ollama daemon (127.0.0.1:11434 if ollama.com website was configured)
            base_url = settings.OLLAMA_BASE_URL
            if "ollama.com" in base_url.lower():
                base_url = "http://127.0.0.1:11434"

            headers = {}
            if settings.OLLAMA_API_KEY:
                headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"

            return ChatOllama(
                model=target_model,
                base_url=base_url,
                temperature=temperature,
                client_kwargs={"headers": headers} if headers else {},
            )

        elif provider == "openai":
            return ChatOpenAI(
                model=target_model if target_model.startswith("gpt") else "gpt-4o",
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature,
            )

        else:
            # Fallback to standard OpenAI compatible client pointing to custom base URL
            return ChatOpenAI(
                model=target_model,
                base_url=settings.OLLAMA_BASE_URL,
                api_key=settings.OLLAMA_API_KEY or "dummy-key",
                temperature=temperature,
            )
