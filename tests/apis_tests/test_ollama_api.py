from types import SimpleNamespace

from agentforge.apis.ollama_api import Ollama


def _stub_logger(model, monkeypatch):
    model.logger = SimpleNamespace(
        log_prompt=lambda *args, **kwargs: None,
        log_response=lambda *args, **kwargs: None,
        warning=lambda *args, **kwargs: None,
        critical=lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(model, "_init_logger", lambda model_prompt, params: None)


def test_generate_preserves_system_and_user_prompt_for_ollama(monkeypatch):
    model = Ollama("gemma4:latest")
    _stub_logger(model, monkeypatch)
    captured = {}

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"response": "provider path works"}

    def fake_post(url, headers, json):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return Response()

    monkeypatch.setattr("agentforge.apis.ollama_api.requests.post", fake_post)

    result = model.generate(
        {"system": "system prompt", "user": "user prompt"},
        host_url="http://localhost:11434/api/generate",
        stream=False,
    )

    assert result == "provider path works"
    assert captured["url"] == "http://localhost:11434/api/generate"
    assert captured["headers"] == {"Content-Type": "application/json"}
    assert captured["json"] == {
        "model": "gemma4:latest",
        "system": "system prompt",
        "prompt": "user prompt",
        "stream": False,
    }
