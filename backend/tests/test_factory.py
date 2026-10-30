import pytest

import llm
from llm.openrouter import OpenRouterLLM


@pytest.fixture(autouse=True)
def fresh_factory(monkeypatch):
    for var in ("LLM_PROVIDER", "OPENROUTER_MODEL", "OPENROUTER_FALLBACK_MODELS"):
        monkeypatch.delenv(var, raising=False)
    llm.get_llm.cache_clear()
    yield
    llm.get_llm.cache_clear()


def test_defaults_to_openrouter_with_fallback():
    provider = llm.get_llm()

    assert isinstance(provider, OpenRouterLLM)
    assert provider.models == [llm.DEFAULT_MODEL, llm.DEFAULT_FALLBACK_MODELS]


def test_model_list_from_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_MODEL", "a/one")
    monkeypatch.setenv("OPENROUTER_FALLBACK_MODELS", " b/two, ,c/three ")

    assert llm.get_llm().models == ["a/one", "b/two", "c/three"]


def test_fallbacks_can_be_disabled(monkeypatch):
    monkeypatch.setenv("OPENROUTER_FALLBACK_MODELS", "")

    assert llm.get_llm().models == [llm.DEFAULT_MODEL]


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nope")

    with pytest.raises(ValueError, match="nope"):
        llm.get_llm()
