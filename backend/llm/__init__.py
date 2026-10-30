"""Model provider selection.

LLM_PROVIDER=openrouter (default): hosted models via OpenRouter, no GPU needed.
LLM_PROVIDER=local: MedGemma via transformers (needs `uv sync --extra local`).
"""

import os
from functools import lru_cache

from .base import LLM, LLMResult, LLMUnavailable

DEFAULT_MODEL = "nvidia/nemotron-3.5-super-vl:free"
DEFAULT_FALLBACK_MODELS = "google/gemma-4-31b-it:free"

__all__ = ["LLM", "LLMResult", "LLMUnavailable", "get_llm"]


@lru_cache
def get_llm() -> LLM:
    provider = os.getenv("LLM_PROVIDER", "openrouter").lower()
    if provider == "local":
        from .local import LocalMedGemmaLLM

        return LocalMedGemmaLLM()
    if provider != "openrouter":
        raise ValueError(f"Unknown LLM_PROVIDER {provider!r}; use 'openrouter' or 'local'.")

    from .openrouter import OpenRouterLLM

    fallbacks = os.getenv("OPENROUTER_FALLBACK_MODELS", DEFAULT_FALLBACK_MODELS)
    return OpenRouterLLM(
        api_key=os.getenv("OPENROUTER_API_KEY", ""),
        models=[os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)]
        + [m.strip() for m in fallbacks.split(",") if m.strip()],
        # Per model; two attempts must fit in the frontend's 60s fetch timeout.
        timeout_s=float(os.getenv("LLM_TIMEOUT_S", "25")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
    )
