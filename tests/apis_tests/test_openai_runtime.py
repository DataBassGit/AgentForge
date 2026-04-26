from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from agentforge.apis.openai_runtime import (
    OpenAIAuthError,
    OpenAIRuntime,
    OpenAIRuntimeError,
)
from agentforge.auth import CodexCredentials


class _FakeResponse:
    def __init__(self, status_code=200, text="", lines=None):
        self.status_code = status_code
        self.text = text
        self._lines = lines or []

    def iter_lines(self, decode_unicode=True):
        for line in self._lines:
            yield line


def test_chat_completions_calls_sdk_client(monkeypatch):
    runtime = OpenAIRuntime()
    create_mock = MagicMock(
        return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="chat-output"))]
        )
    )
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create_mock)))
    monkeypatch.setattr(runtime, "_get_sdk_client", lambda: client)

    out = runtime.chat_completions(
        model="gpt-4o",
        messages=[{"role": "user", "content": "hello"}],
        params={"temperature": 0.4},
    )

    assert out == "chat-output"
    create_mock.assert_called_once_with(
        model="gpt-4o",
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.4,
    )


def test_codex_responses_builds_expected_headers_and_body(monkeypatch):
    runtime = OpenAIRuntime()
    monkeypatch.setattr(
        runtime,
        "_get_codex_credentials",
        lambda: CodexCredentials(account_id="acct_1", access_token="token_1"),
    )

    captured = {}

    def fake_post(url, json, headers, stream, timeout, verify):  # noqa: A002 - test shadow
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["stream"] = stream
        captured["timeout"] = timeout
        captured["verify"] = verify
        return _FakeResponse(
            status_code=200,
            lines=[
                'data: {"type":"response.output_text.delta","delta":"Hello"}',
                "",
                'data: {"type":"response.completed"}',
                "",
            ],
        )

    monkeypatch.setattr("agentforge.apis.openai_runtime.requests.post", fake_post)

    out = runtime.codex_responses(
        model="gpt-5-codex-mini",
        messages=[
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "write code"},
        ],
        params={
            "top_p": 0.2,
            "host_url": "https://example.com/codex",
            "timeout": 12,
            "verify_ssl": False,
        },
    )

    assert out == "Hello"
    assert captured["url"] == "https://example.com/codex"
    assert captured["stream"] is True
    assert captured["timeout"] == 12
    assert captured["verify"] is False
    assert captured["headers"]["Authorization"] == "Bearer token_1"
    assert captured["headers"]["chatgpt-account-id"] == "acct_1"
    assert captured["headers"]["OpenAI-Beta"] == "responses=experimental"
    assert captured["json"]["instructions"] == "sys"
    assert captured["json"]["input"][0]["content"][0]["text"] == "write code"
    assert captured["json"]["top_p"] == 0.2
    assert captured["json"]["text"] == {"verbosity": "medium"}


def test_codex_sse_delta_stream_is_parsed():
    runtime = OpenAIRuntime()
    response = _FakeResponse(
        status_code=200,
        lines=[
            'data: {"type":"response.unknown","value":"noop"}',
            "",
            "data: [DONE]",
            "",
            'data: {"type":"response.output_text.delta","delta":"Hello"}',
            "",
            'data: {"type":"response.output_text.delta","delta":" world"}',
            "",
            'data: {"type":"response.completed"}',
            "",
        ],
    )

    out = runtime._parse_codex_sse(response)
    assert out == "Hello world"


@pytest.mark.parametrize(
    "status_code,response_text,exc_type,match",
    [
        (401, "unauthorized", OpenAIAuthError, "invalid or expired"),
        (403, "forbidden", OpenAIAuthError, "invalid or expired"),
        (429, "rate", OpenAIRuntimeError, "rate-limited"),
        (500, "server boom", OpenAIRuntimeError, "HTTP 500"),
    ],
)
def test_codex_non_200_error_mappings(monkeypatch, status_code, response_text, exc_type, match):
    runtime = OpenAIRuntime()
    monkeypatch.setattr(
        runtime,
        "_get_codex_credentials",
        lambda: CodexCredentials(account_id="acct_1", access_token="token_1"),
    )

    def fake_post(*args, **kwargs):
        return _FakeResponse(status_code=status_code, text=response_text)

    monkeypatch.setattr("agentforge.apis.openai_runtime.requests.post", fake_post)

    with pytest.raises(exc_type, match=match):
        runtime.codex_responses(
            model="gpt-5-codex-mini",
            messages=[{"role": "user", "content": "hi"}],
            params={},
        )


def test_codex_supported_generation_params_are_forwarded(monkeypatch):
    runtime = OpenAIRuntime()
    monkeypatch.setattr(
        runtime,
        "_get_codex_credentials",
        lambda: CodexCredentials(account_id="acct_1", access_token="token_1"),
    )
    captured = {}

    def fake_post(url, json, headers, stream, timeout, verify):  # noqa: A002 - test shadow
        captured["json"] = json
        return _FakeResponse(
            status_code=200,
            lines=[
                'data: {"type":"response.output_text.delta","delta":"ok"}',
                "",
                'data: {"type":"response.completed"}',
                "",
            ],
        )

    monkeypatch.setattr("agentforge.apis.openai_runtime.requests.post", fake_post)

    runtime.codex_responses(
        model="gpt-5-codex-mini",
        messages=[{"role": "user", "content": "hi"}],
        params={
            "top_p": 0.9,
            "reasoning": {"effort": "medium"},
            "text": {"verbosity": "high"},
        },
    )

    assert captured["json"]["top_p"] == 0.9
    assert captured["json"]["reasoning"] == {"effort": "medium"}
    assert captured["json"]["text"] == {"verbosity": "high"}


def test_codex_transport_timeout_and_verify_are_forwarded(monkeypatch):
    runtime = OpenAIRuntime()
    monkeypatch.setattr(
        runtime,
        "_get_codex_credentials",
        lambda: CodexCredentials(account_id="acct_1", access_token="token_1"),
    )
    captured = {}

    def fake_post(url, json, headers, stream, timeout, verify):  # noqa: A002 - test shadow
        captured["timeout"] = timeout
        captured["verify"] = verify
        return _FakeResponse(
            status_code=200,
            lines=[
                'data: {"type":"response.output_text.delta","delta":"ok"}',
                "",
                'data: {"type":"response.completed"}',
                "",
            ],
        )

    monkeypatch.setattr("agentforge.apis.openai_runtime.requests.post", fake_post)

    runtime.codex_responses(
        model="gpt-5-codex-mini",
        messages=[{"role": "user", "content": "hi"}],
        params={"timeout": 33, "verify_ssl": False},
    )

    assert captured["timeout"] == 33
    assert captured["verify"] is False
