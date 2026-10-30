import os
import subprocess
import sys
from pathlib import Path

from llm import LLMUnavailable
from routers.model_api import SYSTEM_PROMPT

BACKEND = Path(__file__).resolve().parents[1]


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_text_question(client, fake_llm):
    response = client.post("/chat/ask", data={"question": "Is 120/80 normal?"})

    assert response.status_code == 200
    assert response.json() == {"result": "fake answer", "filePath": None, "fileName": None}
    messages, images = fake_llm.calls[0]
    assert messages == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Is 120/80 normal?"},
    ]
    assert images is None


def test_image_question(client, fake_llm, png_bytes):
    response = client.post(
        "/chat/ask",
        data={"question": "What do you see?"},
        files={"file": ("scan.png", png_bytes, "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result"] == "fake answer"
    assert body["fileName"] == "scan.png"
    assert body["filePath"].startswith("uploads/users/tester@example.com/")
    assert Path(body["filePath"]).read_bytes() == png_bytes
    _, images = fake_llm.calls[0]
    assert len(images) == 1 and images[0].size == (8, 8)


def test_unsupported_file_type(client, fake_llm):
    response = client.post(
        "/chat/ask",
        data={"question": "?"},
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert fake_llm.calls == []


def test_model_unavailable_returns_503(client, fake_llm):
    fake_llm.error = LLMUnavailable("a: RateLimitError; b: empty response")

    response = client.post("/chat/ask", data={"question": "Hello?"})

    assert response.status_code == 503
    assert "RateLimitError" in response.json()["detail"]


def test_requires_auth(app):
    from fastapi.testclient import TestClient
    from routers.chat_history import get_user_id

    override = app.dependency_overrides.pop(get_user_id)
    try:
        response = TestClient(app).post("/chat/ask", data={"question": "Hi"})
    finally:
        app.dependency_overrides[get_user_id] = override

    assert response.status_code == 401


def test_default_startup_is_light(tmp_path):
    """Importing the app with default settings must not pull in torch/transformers,
    and must create the uploads directory it serves."""
    env = {k: v for k, v in os.environ.items() if k != "LLM_PROVIDER"}
    env["PYTHONPATH"] = str(BACKEND)
    script = (
        "import sys, main\n"
        "from llm import get_llm\n"
        "get_llm()\n"
        "heavy = sorted(m for m in ('torch', 'transformers', 'accelerate') if m in sys.modules)\n"
        "print(heavy)\n"
    )

    result = subprocess.run(
        [sys.executable, "-c", script], cwd=tmp_path, env=env, capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "[]"
    assert (tmp_path / "uploads" / "users").is_dir()
