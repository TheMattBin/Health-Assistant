import os

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from llm import LLMResult


class FakeLLM:
    """Records calls and answers with canned text (or raises `error`)."""

    name = "fake"

    def __init__(self, text="fake answer", error=None):
        self.text = text
        self.error = error
        self.calls = []

    def complete(self, messages, images=None):
        self.calls.append((messages, images))
        if self.error:
            raise self.error
        return LLMResult(text=self.text, model="fake-model", latency_ms=1)


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    # main.py creates uploads/ and chat_history_db/ relative to the cwd.
    os.chdir(tmp_path_factory.mktemp("cwd"))
    import main
    from routers.chat_history import get_user_id

    main.app.dependency_overrides[get_user_id] = lambda: "tester@example.com"
    return main.app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def fake_llm(monkeypatch):
    fake = FakeLLM()
    monkeypatch.setattr("routers.model_api.get_llm", lambda: fake)
    return fake


@pytest.fixture
def png_bytes():
    import io

    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "red").save(buffer, format="PNG")
    return buffer.getvalue()
