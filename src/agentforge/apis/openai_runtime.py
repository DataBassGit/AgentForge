import io
import json
import os
from typing import Any, Dict, Iterable, List, Optional

import requests

from .base_api import NonRetriableModelError
from agentforge.auth.codex_oauth import get_codex_credentials

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - handled at runtime
    OpenAI = None


class OpenAIRuntimeError(Exception):
    """Base runtime exception for OpenAI-family transport calls."""


class OpenAIAuthError(OpenAIRuntimeError, NonRetriableModelError):
    """Raised when required credentials are missing, invalid, or expired."""


class OpenAIDependencyError(OpenAIRuntimeError, NonRetriableModelError):
    """Raised when required optional dependencies are unavailable."""


class OpenAIRuntime:
    """Shared runtime for OpenAI-family providers."""

    DEFAULT_CODEX_URL = "https://chatgpt.com/backend-api/codex/responses"
    DEFAULT_TIMEOUT = 60

    def __init__(self):
        self._sdk_client = None

    def _get_sdk_client(self):
        if self._sdk_client is None:
            if OpenAI is None:
                raise OpenAIDependencyError(
                    "The 'openai' package is required for OpenAI API usage. "
                    "Install dependencies and try again."
                )
            if not os.getenv("OPENAI_API_KEY"):
                raise OpenAIAuthError(
                    "OPENAI_API_KEY is not set. Export OPENAI_API_KEY before using OpenAI API-key models."
                )
            self._sdk_client = OpenAI()
        return self._sdk_client

    def chat_completions(self, model: str, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> str:
        response = self._get_sdk_client().chat.completions.create(
            model=model,
            messages=messages,
            **params,
        )
        return self._extract_chat_content(response)

    def stt(self, model: str, audio_blob: Any, params: Dict[str, Any]) -> str:
        if audio_blob is None:
            raise ValueError("STT generation called without audio data.")

        if isinstance(audio_blob, (bytes, bytearray)):
            audio_file = io.BytesIO(audio_blob)
            audio_file.name = "audio.wav"
        else:
            audio_file = open(audio_blob, "rb")

        try:
            response = self._get_sdk_client().audio.transcriptions.create(
                file=audio_file,
                model=model,
                **params,
            )
        finally:
            try:
                audio_file.close()
            except Exception:  # pragma: no cover - close failures are non-actionable
                pass

        return getattr(response, "text", str(response))

    def tts(self, model: str, input_text: str, params: Dict[str, Any]) -> bytes:
        request_params = dict(params)
        voice = request_params.pop("voice", "alloy")
        audio_format = (
            request_params.pop("response_format", None)
            or request_params.pop("format", None)
            or "wav"
        )
        request_params.pop("format", None)

        response = self._get_sdk_client().audio.speech.create(
            model=model,
            voice=voice,
            input=input_text,
            response_format=audio_format,
            **request_params,
        )
        content = getattr(response, "content", response)
        if isinstance(content, bytes):
            return content
        if isinstance(content, bytearray):
            return bytes(content)
        if isinstance(content, str):
            return content.encode("utf-8")
        try:
            return bytes(content)
        except Exception:
            return str(content).encode("utf-8")

    def codex_responses(self, model: str, messages: List[Dict[str, Any]], params: Dict[str, Any]) -> str:
        credentials = self._get_codex_credentials()
        request_params = dict(params)
        host_url = request_params.pop("host_url", self.DEFAULT_CODEX_URL)
        timeout = request_params.pop("timeout", self.DEFAULT_TIMEOUT)
        verify_ssl = request_params.pop("verify_ssl", True)

        if "max_output_tokens" not in request_params and "max_tokens" in request_params:
            request_params["max_output_tokens"] = request_params.pop("max_tokens")
        else:
            request_params.pop("max_tokens", None)

        instructions, user_text = self._extract_codex_text(messages)
        body = {
            "model": model,
            "store": False,
            "stream": True,
            "instructions": instructions,
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_text}],
                }
            ],
            "text": {"verbosity": "medium"},
        }

        for key in ("max_output_tokens", "temperature", "top_p", "reasoning", "text"):
            if key in request_params:
                body[key] = request_params[key]

        headers = {
            "Authorization": f"Bearer {credentials.access_token}",
            "chatgpt-account-id": credentials.account_id,
            "OpenAI-Beta": "responses=experimental",
            "originator": "agentforge",
            "accept": "text/event-stream",
            "content-type": "application/json",
            "User-Agent": "agentforge (python)",
        }

        response = requests.post(
            host_url,
            json=body,
            headers=headers,
            stream=True,
            timeout=timeout,
            verify=verify_ssl,
        )
        self._raise_for_codex_status(response)
        return self._parse_codex_sse(response)

    @staticmethod
    def _extract_chat_content(response: Any) -> str:
        try:
            content = response.choices[0].message.content
        except Exception:
            return str(response)
        return OpenAIRuntime._content_to_text(content)

    @staticmethod
    def _content_to_text(content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            chunks: List[str] = []
            for part in content:
                if isinstance(part, str):
                    chunks.append(part)
                    continue
                if not isinstance(part, dict):
                    continue
                if isinstance(part.get("text"), str):
                    chunks.append(part["text"])
                    continue
                if part.get("type") == "input_text" and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
            return "".join(chunks)
        return str(content)

    def _get_codex_credentials(self):
        try:
            return get_codex_credentials(interactive=False, force_reauth=False)
        except NonRetriableModelError:
            raise
        except Exception as exc:
            message = str(exc)
            if "oauth-cli-kit" in message:
                raise OpenAIDependencyError(message) from exc
            raise OpenAIAuthError(message) from exc

    @classmethod
    def _extract_codex_text(cls, messages: List[Dict[str, Any]]) -> tuple[str, str]:
        instructions = ""
        user_chunks: List[str] = []
        for message in messages or []:
            role = message.get("role")
            text = cls._content_to_text(message.get("content"))
            if role == "system" and not instructions:
                instructions = text
            if role == "user":
                user_chunks.append(text)
        user_text = "\n".join(chunk for chunk in user_chunks if chunk)
        return instructions or "", user_text or ""

    @staticmethod
    def _raise_for_codex_status(response: requests.Response) -> None:
        if response.status_code == 200:
            return

        body_excerpt = (response.text or "").strip().replace("\n", " ")
        body_excerpt = body_excerpt[:200]

        if response.status_code in (401, 403):
            raise OpenAIAuthError("OAuth token invalid or expired; run `python -m agentforge.init_codex_oauth`.")
        if response.status_code == 429:
            raise OpenAIRuntimeError("Codex request was rate-limited (HTTP 429). Check quota and retry.")
        raise OpenAIRuntimeError(
            f"Codex request failed with HTTP {response.status_code}. Response excerpt: {body_excerpt}"
        )

    def _parse_codex_sse(self, response: requests.Response) -> str:
        output_chunks: List[str] = []
        completed = False

        for event in self._iter_sse_events(response.iter_lines(decode_unicode=True)):
            if not event:
                continue

            event_type = event.get("type")
            if event_type == "response.output_text.delta":
                delta = event.get("delta", "")
                if isinstance(delta, dict):
                    delta = delta.get("text", "")
                if isinstance(delta, str):
                    output_chunks.append(delta)
                continue
            if event_type == "response.completed":
                completed = True
                break
            if event_type in {"error", "response.failed"}:
                error_message = self._extract_event_error(event)
                raise OpenAIRuntimeError(f"Codex response failed: {error_message}")

        if not completed and not output_chunks:
            raise OpenAIRuntimeError("Codex response stream ended before completion.")
        return "".join(output_chunks)

    @staticmethod
    def _extract_event_error(event: Dict[str, Any]) -> str:
        if isinstance(event.get("error"), dict):
            message = event["error"].get("message")
            if isinstance(message, str) and message:
                return message
        for key in ("message", "detail"):
            value = event.get(key)
            if isinstance(value, str) and value:
                return value
        return "Unknown Codex error."

    @staticmethod
    def _iter_sse_events(lines: Iterable[str]) -> Iterable[Dict[str, Any]]:
        frame_lines: List[str] = []
        for raw_line in lines:
            if raw_line is None:
                continue
            line = raw_line if isinstance(raw_line, str) else raw_line.decode("utf-8")
            if line == "":
                event = OpenAIRuntime._parse_sse_frame(frame_lines)
                frame_lines = []
                if event is not None:
                    yield event
                continue
            frame_lines.append(line)

        tail_event = OpenAIRuntime._parse_sse_frame(frame_lines)
        if tail_event is not None:
            yield tail_event

    @staticmethod
    def _parse_sse_frame(frame_lines: List[str]) -> Optional[Dict[str, Any]]:
        if not frame_lines:
            return None
        data_chunks = []
        for line in frame_lines:
            if line.startswith("data:"):
                data_chunks.append(line[5:].strip())
        if not data_chunks:
            return None
        payload = "\n".join(data_chunks).strip()
        if not payload or payload == "[DONE]":
            return None
        try:
            loaded = json.loads(payload)
            if isinstance(loaded, dict):
                return loaded
        except json.JSONDecodeError:
            return None
        return None
