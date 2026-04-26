from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agentforge.apis.base_api import NonRetriableModelError
from agentforge.apis.openai_api import Codex
from agentforge.apis.openai_runtime import OpenAIAuthError


def _stub_logger(model, monkeypatch):
    model.logger = SimpleNamespace(
        log_prompt=lambda *args, **kwargs: None,
        log_response=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
        critical=lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(model, "_init_logger", lambda model_prompt, params: None)


def test_codex_generate_returns_runtime_output(monkeypatch):
    model = Codex("gpt-5-codex-mini")
    _stub_logger(model, monkeypatch)
    mock = MagicMock(return_value="runtime-output")
    monkeypatch.setattr(model.runtime, "codex_responses", mock)

    out = model.generate({"system": "sys", "user": "hello"})

    assert out == "runtime-output"


def test_codex_prompt_conversion_uses_base_model_message_format(monkeypatch):
    model = Codex("gpt-5-codex-mini")
    _stub_logger(model, monkeypatch)
    captured = {}

    def fake_codex_responses(model, messages, params):
        captured["model"] = model
        captured["messages"] = messages
        captured["params"] = params
        return "ok"

    monkeypatch.setattr(model.runtime, "codex_responses", fake_codex_responses)

    out = model.generate({"system": "system prompt", "user": "user prompt"}, top_p=0.3)

    assert out == "ok"
    assert captured["model"] == "gpt-5-codex-mini"
    assert captured["messages"][0] == {"role": "system", "content": "system prompt"}
    assert captured["messages"][1] == {"role": "user", "content": "user prompt"}
    assert captured["params"]["top_p"] == 0.3


def test_codex_auth_failure_is_non_retriable(monkeypatch):
    model = Codex("gpt-5-codex-mini")
    _stub_logger(model, monkeypatch)
    mock = MagicMock(side_effect=OpenAIAuthError("token expired"))
    monkeypatch.setattr(model.runtime, "codex_responses", mock)

    with pytest.raises(NonRetriableModelError, match="token expired"):
        model.generate({"system": "sys", "user": "hello"})

    assert mock.call_count == 1
