import base64
import io
from types import SimpleNamespace

import httpx
import openai
import pytest
from PIL import Image

from llm import LLMUnavailable
from llm.openrouter import MAX_IMAGE_SIDE, OpenRouterLLM

MESSAGES = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "What is in this image?"},
]


class FakeCompletions:
    """Stands in for client.chat.completions; `replies` maps model -> text or exception."""

    def __init__(self, replies):
        self.replies = replies
        self.calls = []

    def create(self, *, model, messages, **kwargs):
        self.calls.append({"model": model, "messages": messages, **kwargs})
        reply = self.replies[model]
        if isinstance(reply, Exception):
            raise reply
        message = SimpleNamespace(content=reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def make_llm(replies, api_key="sk-test"):
    completions = FakeCompletions(replies)
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return OpenRouterLLM(api_key=api_key, models=list(replies), client=client), completions


def rate_limited():
    request = httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions")
    response = httpx.Response(429, request=request)
    return openai.RateLimitError("rate limited", response=response, body=None)


def test_first_model_answers():
    llm, completions = make_llm({"primary": "Looks normal.", "backup": "unused"})

    result = llm.complete(MESSAGES)

    assert result.text == "Looks normal."
    assert result.model == "primary"
    assert [c["model"] for c in completions.calls] == ["primary"]
    assert completions.calls[0]["messages"] == MESSAGES


def test_falls_back_after_api_error():
    llm, completions = make_llm({"primary": rate_limited(), "backup": "From backup."})

    result = llm.complete(MESSAGES)

    assert (result.text, result.model) == ("From backup.", "backup")
    assert [c["model"] for c in completions.calls] == ["primary", "backup"]


@pytest.mark.parametrize("empty", [None, "", "   ", "<think>only reasoning</think>"])
def test_falls_back_on_empty_answer(empty):
    llm, _ = make_llm({"primary": empty, "backup": "Real answer."})

    assert llm.complete(MESSAGES).model == "backup"


def test_strips_think_blocks():
    llm, _ = make_llm({"primary": "<think>hmm</think>\nDrink water."})

    assert llm.complete(MESSAGES).text == "Drink water."


def test_all_models_failing_raises_with_reasons():
    llm, _ = make_llm({"primary": rate_limited(), "backup": ""})

    with pytest.raises(LLMUnavailable, match="primary: RateLimitError; backup: empty response"):
        llm.complete(MESSAGES)


def test_missing_api_key_raises_without_calling_api():
    llm, completions = make_llm({"primary": "unused"}, api_key="")

    with pytest.raises(LLMUnavailable, match="OPENROUTER_API_KEY"):
        llm.complete(MESSAGES)
    assert completions.calls == []


def test_images_become_data_url_parts_on_last_user_message():
    llm, completions = make_llm({"primary": "ok"})
    big = Image.new("RGBA", (MAX_IMAGE_SIDE * 2, MAX_IMAGE_SIDE), (0, 0, 255, 255))

    llm.complete(MESSAGES, [big])

    sent = completions.calls[0]["messages"]
    assert sent[0] == MESSAGES[0]
    text_part, image_part = sent[1]["content"]
    assert text_part == {"type": "text", "text": "What is in this image?"}
    url = image_part["image_url"]["url"]
    assert url.startswith("data:image/png;base64,")
    decoded = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
    assert decoded.mode == "RGB"
    assert max(decoded.size) == MAX_IMAGE_SIDE
    # The caller's messages are left untouched.
    assert MESSAGES[1]["content"] == "What is in this image?"
    assert big.size == (MAX_IMAGE_SIDE * 2, MAX_IMAGE_SIDE)
