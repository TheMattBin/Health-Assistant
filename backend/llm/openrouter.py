"""OpenRouter chat client with ordered model fallback.

Free OpenRouter models are rate-limited and come and go, so every call walks
the configured model list until one returns usable text.
"""

import base64
import io
import logging
import re
from time import perf_counter
from typing import List, Optional

import openai
from PIL import Image

from .base import LLMResult, LLMUnavailable

log = logging.getLogger(__name__)

_THINK = re.compile(r"<think>.*?(</think>|$)", re.DOTALL | re.IGNORECASE)
# Keeps uploads (e.g. 300 dpi PDF pages) well within provider payload limits.
MAX_IMAGE_SIDE = 1600


class OpenRouterLLM:
    def __init__(
        self,
        *,
        api_key: str,
        models: List[str],
        base_url: str = "https://openrouter.ai/api/v1",
        timeout_s: float = 25.0,
        max_tokens: int = 1000,
        client=None,
    ):
        self.name = "openrouter"
        self.models = models
        self.max_tokens = max_tokens
        self.configured = bool(api_key)
        self._client = client or openai.OpenAI(
            api_key=api_key or "not-set",
            base_url=base_url,
            timeout=timeout_s,
            # The model list is the retry policy; SDK retries would honour
            # Retry-After on 429s and blow the frontend's 60s request budget.
            max_retries=0,
            default_headers={"X-Title": "AI Health Assistant"},
        )

    def complete(
        self, messages: List[dict], images: Optional[List[Image.Image]] = None
    ) -> LLMResult:
        if not self.configured:
            raise LLMUnavailable("OPENROUTER_API_KEY is not set.")
        payload = _attach_images(messages, images or [])
        failures = []
        for model in self.models:
            started = perf_counter()
            try:
                response = self._client.chat.completions.create(
                    model=model, messages=payload, temperature=0.2, max_tokens=self.max_tokens
                )
            except openai.APIError as exc:
                log.warning("LLM call to %s failed: %s", model, exc)
                failures.append(f"{model}: {type(exc).__name__}")
                continue
            choice = response.choices[0] if response.choices else None
            text = _THINK.sub("", (choice.message.content if choice else None) or "").strip()
            if not text:
                failures.append(f"{model}: empty response")
                continue
            return LLMResult(text=text, model=model, latency_ms=int((perf_counter() - started) * 1000))
        raise LLMUnavailable("; ".join(failures))


def _attach_images(messages: List[dict], images: List[Image.Image]) -> List[dict]:
    """Turn the last user message into text + image_url content parts."""
    if not images:
        return messages
    *head, last = messages
    parts = [{"type": "text", "text": last["content"]}]
    parts += [{"type": "image_url", "image_url": {"url": _data_url(img)}} for img in images]
    return [*head, {**last, "content": parts}]


def _data_url(image: Image.Image) -> str:
    image = image.convert("RGB") if image.mode not in ("RGB", "L") else image.copy()
    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
