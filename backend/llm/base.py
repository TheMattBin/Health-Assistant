from dataclasses import dataclass
from typing import List, Optional, Protocol

from PIL import Image


class LLMUnavailable(Exception):
    """No configured model produced a response."""


@dataclass
class LLMResult:
    text: str
    model: str
    latency_ms: int


class LLM(Protocol):
    """A chat model. Messages use the OpenAI shape ({"role", "content": str});
    images are attached to the last user message."""

    name: str

    def complete(
        self, messages: List[dict], images: Optional[List[Image.Image]] = None
    ) -> LLMResult: ...
