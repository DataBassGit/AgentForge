from types import SimpleNamespace

import pytest

from agentforge.apis.anthropic_api import Claude
from agentforge.apis.base_api import ModelResponseError, NonRetriableModelError
from agentforge.apis.gemini_api import Gemini
from agentforge.apis.groq_api import GroqAPI
from agentforge.apis.lm_studio_api import LMStudio
from agentforge.apis.ollama_api import Ollama
from agentforge.apis.openrouter_api import OpenRouter
from agentforge.apis.vllm_api import VLLM


class _Response:
    def __init__(self, status_code=200, text="", payload=None):
        self.status_code = status_code
        self.text = text
        self._payload = payload or {"choices": [{"message": {"content": "ok"}}]}

    def json(self):
        return self._payload


def test_model_response_error_keeps_value_error_compatibility():
    assert issubclass(ModelResponseError, ValueError)
    assert issubclass(ModelResponseError, NonRetriableModelError)


@pytest.mark.parametrize(
    ("env_var", "provider", "prompt"),
    [
        ("ANTHROPIC_API_KEY", Claude("claude-test"), {"messages": [{"role": "user", "content": "hi"}]}),
        ("GOOGLE_API_KEY", Gemini("gemini-test"), {"messages": [{"role": "user", "content": "hi"}]}),
        ("GROQ_API_KEY", GroqAPI("groq-test"), [{"role": "user", "content": "hi"}]),
        ("OPENROUTER_API_KEY", OpenRouter("openrouter-test"), {"messages": [{"role": "user", "content": "hi"}]}),
    ],
)
def test_missing_provider_api_keys_fail_before_network(monkeypatch, env_var, provider, prompt):
    monkeypatch.delenv(env_var, raising=False)

    with pytest.raises(NonRetriableModelError, match=env_var):
        provider._do_api_call(prompt)


@pytest.mark.parametrize(
    ("module_path", "provider", "prompt"),
    [
        ("agentforge.apis.ollama_api.requests.post", Ollama("ollama-test"), {"system": "s", "user": "u"}),
        ("agentforge.apis.lm_studio_api.requests.post", LMStudio("lm-test"), {"messages": []}),
        ("agentforge.apis.vllm_api.requests.post", VLLM("vllm-test"), {"messages": []}),
    ],
)
def test_local_openai_compatible_non_200_errors_are_diagnostic(monkeypatch, module_path, provider, prompt):
    monkeypatch.setattr(module_path, lambda *args, **kwargs: _Response(status_code=500, text="service failed"))

    with pytest.raises(ModelResponseError, match="HTTP 500"):
        provider._do_api_call(prompt)


def test_openrouter_non_200_error_is_diagnostic(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(
        "agentforge.apis.openrouter_api.requests.post",
        lambda *args, **kwargs: _Response(status_code=401, text="bad key"),
    )

    with pytest.raises(ModelResponseError, match="HTTP 401"):
        OpenRouter("openrouter-test")._do_api_call({"messages": []})


def test_openrouter_unwraps_base_model_message_payload(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    captured = {}

    def fake_post(url, headers, json):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _Response()

    monkeypatch.setattr("agentforge.apis.openrouter_api.requests.post", fake_post)

    response = OpenRouter("openrouter-test")._do_api_call(
        {"messages": [{"role": "user", "content": "hi"}]}, http_referer="https://agentforge.local", temperature=0.2
    )

    assert response == {"choices": [{"message": {"content": "ok"}}]}
    assert captured["json"]["messages"] == [{"role": "user", "content": "hi"}]
    assert captured["json"]["temperature"] == 0.2
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["headers"]["HTTP-Referer"] == "https://agentforge.local"


def test_groq_unwraps_base_model_message_payload_and_modernizes_token_param(monkeypatch):
    create_calls = []

    def fake_create(**kwargs):
        create_calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))])

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create)))
    provider = GroqAPI("groq-test")
    monkeypatch.setattr(provider, "_get_client", lambda: client)

    response = provider._do_api_call({"messages": [{"role": "user", "content": "hi"}]}, max_tokens=64, temperature=0.2)

    assert provider._process_response(response) == "ok"
    assert create_calls == [
        {
            "model": "groq-test",
            "messages": [{"role": "user", "content": "hi"}],
            "max_completion_tokens": 64,
            "temperature": 0.2,
        }
    ]


@pytest.mark.parametrize(
    ("provider", "raw_response", "match"),
    [
        (Claude("claude-test"), SimpleNamespace(content=[]), "malformed"),
        (Gemini("gemini-test"), SimpleNamespace(text=" "), "empty"),
        (GroqAPI("groq-test"), SimpleNamespace(choices=[]), "malformed"),
        (Ollama("ollama-test"), {"unexpected": "shape"}, "malformed"),
        (OpenRouter("openrouter-test"), {"error": {"code": 400, "message": "bad request"}}, "bad request"),
        (LMStudio("lm-test"), {}, "malformed"),
        (VLLM("vllm-test"), {}, "malformed"),
    ],
)
def test_malformed_provider_responses_raise_model_response_error(provider, raw_response, match):
    with pytest.raises(ModelResponseError, match=match):
        provider._process_response(raw_response)
