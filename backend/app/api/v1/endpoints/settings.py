"""Settings and Live Model Integrator Pulse Endpoints."""

import time
import httpx
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException

from app.schemas.settings import (
    SettingsConfig,
    SettingsUpdate,
    ModelStatusResponse,
    ModelTestRequest,
    ModelTestResponse,
)
from app.core.config import settings, sync_env_file
from app.core.logging import logger

router = APIRouter()


def _mask_key(key: str) -> Optional[str]:
    """Helper to mask secret API keys for safe UI display."""
    if not key:
        return None
    if len(key) <= 8:
        return "••••••••"
    return f"{key[:4]}••••••••{key[-4:]}"


@router.get("/", response_model=SettingsConfig)
async def get_settings():
    """Retrieve current system configuration with masked API keys."""
    return SettingsConfig(
        llm_provider=settings.LLM_PROVIDER,
        ollama_base_url=settings.OLLAMA_BASE_URL,
        ollama_api_key_masked=_mask_key(settings.OLLAMA_API_KEY),
        default_model=settings.DEFAULT_MODEL,
        fast_model=settings.FAST_MODEL,
        openai_api_key_masked=_mask_key(settings.OPENAI_API_KEY),
        highlight_color=settings.PLAYWRIGHT_HIGHLIGHT_COLOR,
        highlight_outline_width=settings.PLAYWRIGHT_HIGHLIGHT_OUTLINE_WIDTH,
        viewport_width=settings.PLAYWRIGHT_VIEWPORT_WIDTH,
        viewport_height=settings.PLAYWRIGHT_VIEWPORT_HEIGHT,
        screencast_fps=settings.SCREENCAST_FPS,
        screencast_quality=settings.SCREENCAST_QUALITY,
        environment=settings.ENVIRONMENT,
        backend_port=settings.BACKEND_PORT,
    )


@router.put("/", response_model=SettingsConfig)
async def update_settings(payload: SettingsUpdate):
    """Dynamically update runtime settings and synchronize with .env file on disk."""
    env_updates = {}

    if payload.llm_provider is not None:
        settings.LLM_PROVIDER = payload.llm_provider
        env_updates["LLM_PROVIDER"] = payload.llm_provider
    if payload.ollama_base_url is not None:
        cleaned_url = payload.ollama_base_url.rstrip("/")
        settings.OLLAMA_BASE_URL = cleaned_url
        env_updates["OLLAMA_BASE_URL"] = cleaned_url
    if payload.ollama_api_key is not None:
        settings.OLLAMA_API_KEY = payload.ollama_api_key
        # Always write key to .env — empty string clears it
        env_updates["OLLAMA_API_KEY"] = payload.ollama_api_key
    if payload.default_model is not None:
        settings.DEFAULT_MODEL = payload.default_model
        env_updates["DEFAULT_MODEL"] = payload.default_model
    if payload.fast_model is not None:
        settings.FAST_MODEL = payload.fast_model
        env_updates["FAST_MODEL"] = payload.fast_model
    if payload.openai_api_key is not None:
        settings.OPENAI_API_KEY = payload.openai_api_key
        # Always write to .env — empty string clears it
        env_updates["OPENAI_API_KEY"] = payload.openai_api_key

    if payload.highlight_color is not None:
        settings.PLAYWRIGHT_HIGHLIGHT_COLOR = payload.highlight_color
        env_updates["PLAYWRIGHT_HIGHLIGHT_COLOR"] = payload.highlight_color
    if payload.viewport_width is not None:
        settings.PLAYWRIGHT_VIEWPORT_WIDTH = payload.viewport_width
        env_updates["PLAYWRIGHT_VIEWPORT_WIDTH"] = str(payload.viewport_width)
    if payload.viewport_height is not None:
        settings.PLAYWRIGHT_VIEWPORT_HEIGHT = payload.viewport_height
        env_updates["PLAYWRIGHT_VIEWPORT_HEIGHT"] = str(payload.viewport_height)
    if payload.screencast_fps is not None:
        settings.SCREENCAST_FPS = payload.screencast_fps
        env_updates["SCREENCAST_FPS"] = str(payload.screencast_fps)
    if payload.screencast_quality is not None:
        settings.SCREENCAST_QUALITY = payload.screencast_quality
        env_updates["SCREENCAST_QUALITY"] = str(payload.screencast_quality)

    # Persist and synchronize to .env file
    if env_updates:
        try:
            sync_env_file(env_updates)
            logger.info(f"Synchronized {len(env_updates)} settings to root .env file.")
        except Exception as e:
            logger.warning(f"Could not write to .env file: {e}")

    logger.info(f"Runtime settings updated: Provider={settings.LLM_PROVIDER}, Model={settings.DEFAULT_MODEL}, BaseURL={settings.OLLAMA_BASE_URL}")
    return await get_settings()


def _build_ollama_api_url(base_url: str, path: str) -> str:
    """Construct a correct Ollama API URL regardless of how base_url is configured.

    Handles cases like:
      - http://localhost:11434        → http://localhost:11434/api/tags
      - http://localhost:11434/api    → http://localhost:11434/api/tags
      - https://ollama.com            → NOT a real API; caller should use local daemon
      - https://ollama.com/api        → NOT a real API; caller should use local daemon
    """
    url = base_url.rstrip("/")
    if url.endswith("/api"):
        return f"{url}/{path.lstrip('/')}"
    return f"{url}/api/{path.lstrip('/')}"


def _is_real_ollama_server(base_url: str) -> bool:
    """Return True if the base_url points to an actual Ollama API server (not the website)."""
    url = base_url.lower()
    # ollama.com is the model library website — it has no generate/tags API
    return "ollama.com" not in url


@router.get("/models")
async def get_available_models():
    """Discover live models from the local Ollama daemon.

    Ollama Cloud models (e.g. gemma4:cloud, glm-5.1:cloud) are proxied through
    the local Ollama daemon — there is no separate HTTP API on ollama.com.
    We therefore always query localhost:11434 as the primary source and optionally
    also the configured base_url if it is a real Ollama server.
    """
    discovered: list[str] = []

    headers: dict = {}
    if settings.OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"

    async def _fetch_tags(url: str, extra_headers: dict | None = None) -> list[str]:
        """Probe an Ollama /api/tags endpoint and return model names."""
        names: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(url, headers=extra_headers or {})
                if resp.status_code == 200:
                    for m in resp.json().get("models", []):
                        name = m.get("name", "")
                        caps = m.get("capabilities") or m.get("details", {}).get("capabilities", [])
                        # Exclude pure embedding models from the generation model list
                        if name and caps != ["embedding"]:
                            names.append(name)
        except Exception as exc:
            logger.debug(f"Could not fetch Ollama tags from {url}: {exc}")
        return names

    # 1. Always probe local Ollama daemon first (handles both local and cloud models)
    local_models = await _fetch_tags("http://127.0.0.1:11434/api/tags")
    for m in local_models:
        if m not in discovered:
            discovered.append(m)

    # 2. Also probe the configured base_url if it's a real Ollama server (not ollama.com)
    configured_url = settings.OLLAMA_BASE_URL.rstrip("/")
    if _is_real_ollama_server(configured_url) and configured_url not in ("http://127.0.0.1:11434", "http://localhost:11434"):
        tags_url = _build_ollama_api_url(configured_url, "tags")
        extra_models = await _fetch_tags(tags_url, extra_headers=headers)
        for m in extra_models:
            if m not in discovered:
                discovered.append(m)

    # 3. Fallback: well-known models if Ollama is completely unreachable
    if not discovered:
        logger.warning("Ollama unreachable — returning fallback model list")
        discovered = [
            "qwen2.5:7b",
            "llama3.1:8b",
            "llama3.3:70b",
            "gemma4:12b",
            "qwen2.5-coder:latest",
            "deepseek-coder-v2:latest",
            "deepseek-r1:70b",
        ]

    return {
        "success": True,
        "models": discovered,
        "count": len(discovered),
        "current_model": settings.DEFAULT_MODEL,
        "source": "local_daemon" if local_models else "fallback",
    }



@router.get("/model-status", response_model=ModelStatusResponse)
async def get_model_pulse_status():
    """Live pulse endpoint — checks LLM integrator availability and latency.

    For ollama_cloud: cloud models are served by the local daemon, so we always
    probe 127.0.0.1:11434, never ollama.com directly.
    """
    start_time = time.perf_counter()
    provider = settings.LLM_PROVIDER
    model = settings.DEFAULT_MODEL
    now_iso = datetime.utcnow().isoformat()

    if provider in ("ollama_local", "ollama_cloud", "ollama"):
        # Always hit the local Ollama daemon — it handles both local and cloud models
        daemon_url = "http://127.0.0.1:11434"

        # If provider is explicitly local with a non-default URL, respect it
        configured = settings.OLLAMA_BASE_URL.rstrip("/")
        if provider == "ollama_local" and _is_real_ollama_server(configured):
            daemon_url = configured

        tags_url = _build_ollama_api_url(daemon_url, "tags")
        headers: dict = {}
        if settings.OLLAMA_API_KEY:
            headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(tags_url, headers=headers)
                latency = round((time.perf_counter() - start_time) * 1000, 1)

                if resp.status_code == 200:
                    data = resp.json()
                    installed = [m.get("name", "") for m in data.get("models", [])]
                    model_found = any(
                        m == model or m.startswith(model.split(":")[0])
                        for m in installed
                    )

                    status = "online" if latency <= 2500 else "degraded"
                    msg = f"Ollama daemon online at {daemon_url} · {len(installed)} models available"
                    if not model_found and installed:
                        msg += f" · Note: '{model}' not pulled yet (run: ollama pull {model})"

                    return ModelStatusResponse(
                        status=status,
                        provider=provider,
                        model_name=model,
                        latency_ms=latency,
                        last_ping=now_iso,
                        message=msg,
                        capabilities=["chat", "structured_output", "json_mode"],
                    )
                else:
                    latency = round((time.perf_counter() - start_time) * 1000, 1)
                    return ModelStatusResponse(
                        status="offline",
                        provider=provider,
                        model_name=model,
                        latency_ms=latency,
                        last_ping=now_iso,
                        message=f"Ollama returned HTTP {resp.status_code} from {daemon_url}",
                        capabilities=[],
                    )
        except Exception as exc:
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            return ModelStatusResponse(
                status="offline",
                provider=provider,
                model_name=model,
                latency_ms=latency,
                last_ping=now_iso,
                message=f"Cannot reach Ollama at {daemon_url} — ensure Ollama is running: ollama serve",
                capabilities=[],
            )


    # For OpenAI / other providers — assume online if key is configured
    return ModelStatusResponse(
        status="online" if settings.OPENAI_API_KEY else "degraded",
        provider=provider,
        model_name=model,
        latency_ms=0.0,
        last_ping=now_iso,
        message="OpenAI provider configured" if settings.OPENAI_API_KEY else "OpenAI API key not set",
        capabilities=["chat", "structured_output"],
    )


@router.post("/test-model", response_model=ModelTestResponse)
async def test_model_connection(payload: ModelTestRequest):
    """On-demand connection test — uses a fast /api/tags ping for Ollama providers.

    For ollama_cloud: the cloud models run through the local Ollama daemon, so
    we always test against the local daemon (127.0.0.1:11434), not ollama.com.
    For openai/litellm: tests with a lightweight chat completion.
    """
    target_provider = payload.provider or settings.LLM_PROVIDER
    target_model = payload.model_name or settings.DEFAULT_MODEL
    raw_base_url = (payload.base_url or settings.OLLAMA_BASE_URL).rstrip("/")
    start_time = time.perf_counter()

    api_key = payload.api_key or settings.OLLAMA_API_KEY
    headers: dict = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    # ── Ollama (local OR cloud) ──────────────────────────────────────────────
    if target_provider in ("ollama_local", "ollama_cloud", "ollama"):
        # Cloud models (gemma4:cloud etc.) are actually served by the local Ollama
        # daemon — there is no direct HTTP API on ollama.com.
        # Always ping the local daemon; also try the configured URL if it's a
        # real Ollama server (not the ollama.com website).

        candidate_urls: list[str] = ["http://127.0.0.1:11434"]
        if _is_real_ollama_server(raw_base_url) and raw_base_url not in (
            "http://127.0.0.1:11434", "http://localhost:11434"
        ):
            candidate_urls.append(raw_base_url)

        last_error: str = ""
        for daemon_url in candidate_urls:
            tags_url = _build_ollama_api_url(daemon_url, "tags")
            try:
                async with httpx.AsyncClient(timeout=6.0) as client:
                    resp = await client.get(tags_url, headers=headers)
                    latency = round((time.perf_counter() - start_time) * 1000, 1)

                    if resp.status_code == 200:
                        data = resp.json()
                        installed = [m.get("name", "") for m in data.get("models", [])]
                        model_found = any(
                            m == target_model or m.startswith(target_model.split(":")[0])
                            for m in installed
                        )

                        if model_found:
                            return ModelTestResponse(
                                success=True,
                                latency_ms=latency,
                                provider=target_provider,
                                model_name=target_model,
                                sample_response=(
                                    f"Ollama daemon online at {daemon_url}. "
                                    f"Model '{target_model}' confirmed installed. "
                                    f"{len(installed)} models available."
                                ),
                            )
                        else:
                            available_preview = ", ".join(installed[:5]) + ("…" if len(installed) > 5 else "")
                            return ModelTestResponse(
                                success=False,
                                latency_ms=latency,
                                provider=target_provider,
                                model_name=target_model,
                                error_message=(
                                    f"Ollama daemon is online at {daemon_url} but model "
                                    f"'{target_model}' is not installed. "
                                    f"Run: ollama pull {target_model}. "
                                    f"Available: {available_preview}"
                                ),
                            )
                    else:
                        last_error = f"HTTP {resp.status_code} from {daemon_url}"
            except Exception as exc:
                last_error = f"Cannot reach {daemon_url}: {exc}"
                logger.debug(f"Ollama ping failed for {daemon_url}: {exc}")

        latency = round((time.perf_counter() - start_time) * 1000, 1)
        return ModelTestResponse(
            success=False,
            latency_ms=latency,
            provider=target_provider,
            model_name=target_model,
            error_message=(
                f"Could not reach Ollama daemon. {last_error}. "
                "Ensure Ollama is running: ollama serve"
            ),
        )

    # ── OpenAI ──────────────────────────────────────────────────────────────
    if target_provider == "openai":
        openai_key = payload.api_key or settings.OPENAI_API_KEY
        if not openai_key:
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            return ModelTestResponse(
                success=False, latency_ms=latency,
                provider=target_provider, model_name=target_model,
                error_message="OPENAI_API_KEY is not set. Add it in the API Key field.",
            )
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                    json={"model": target_model, "messages": [{"role": "user", "content": "Say: DocuAgent Connected"}], "max_tokens": 10},
                )
                latency = round((time.perf_counter() - start_time) * 1000, 1)
                if resp.status_code == 200:
                    reply = resp.json()["choices"][0]["message"]["content"].strip()
                    return ModelTestResponse(success=True, latency_ms=latency, provider=target_provider,
                                             model_name=target_model, sample_response=reply)
                else:
                    return ModelTestResponse(success=False, latency_ms=latency, provider=target_provider,
                                             model_name=target_model,
                                             error_message=f"OpenAI HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as exc:
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            return ModelTestResponse(success=False, latency_ms=latency, provider=target_provider,
                                     model_name=target_model, error_message=str(exc))

    # ── LiteLLM / other ─────────────────────────────────────────────────────
    try:
        gen_url = _build_ollama_api_url(raw_base_url, "generate")
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                gen_url,
                json={"model": target_model, "prompt": "Say: DocuAgent Connected", "stream": False},
                headers=headers,
            )
            latency = round((time.perf_counter() - start_time) * 1000, 1)
            if resp.status_code == 200:
                data = resp.json()
                return ModelTestResponse(success=True, latency_ms=latency, provider=target_provider,
                                         model_name=target_model,
                                         sample_response=data.get("response", "Connected.").strip())
            return ModelTestResponse(success=False, latency_ms=latency, provider=target_provider,
                                     model_name=target_model,
                                     error_message=f"HTTP {resp.status_code}: {resp.text[:150]}")
    except Exception as exc:
        latency = round((time.perf_counter() - start_time) * 1000, 1)
        return ModelTestResponse(success=False, latency_ms=latency, provider=target_provider,
                                 model_name=target_model,
                                 error_message=f"Could not connect to {raw_base_url}: {exc}")

