from .base_api import BaseModel
from .openai_runtime import OpenAIRuntime
from agentforge.apis.mixins.audio_input_mixin import AudioInputMixin
from agentforge.apis.mixins.audio_output_mixin import AudioOutputMixin


class _OpenAIBaseModel(BaseModel):
    """Shared setup for OpenAI-family model wrappers."""

    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)
        self.runtime = OpenAIRuntime()


class GPT(_OpenAIBaseModel):
    """Concrete implementation for OpenAI GPT models."""

    def _do_api_call(self, prompt, **filtered_params):
        messages = prompt["messages"] if isinstance(prompt, dict) and "messages" in prompt else prompt
        return self.runtime.chat_completions(
            model=self.model_name,
            messages=messages,
            params=filtered_params,
        )

    def _process_response(self, raw_response):
        return raw_response


class O1Series(GPT):
    """OpenAI O-series wrapper with custom prompt shaping."""

    def _prepare_prompt(self, model_prompt):
        content = f"{model_prompt.get('system', '')}\n\n{model_prompt.get('user', '')}"
        return [{"role": "user", "content": content}]


class STT(AudioInputMixin, _OpenAIBaseModel):
    """Speech-to-Text wrapper around OpenAI Whisper models."""

    def _merge_parts(self, parts, **params):
        return {"audio": parts.get("audio")}

    def _do_api_call(self, prompt, **filtered_params):
        audio_blob = prompt.get("audio")
        return self.runtime.stt(
            model=self.model_name,
            audio_blob=audio_blob,
            params=filtered_params,
        )

    def _process_response(self, raw_response):
        return raw_response


class TTS(AudioOutputMixin, _OpenAIBaseModel):
    """Text-to-Speech wrapper producing audio bytes."""

    def _do_api_call(self, prompt, **filtered_params):
        if isinstance(prompt, dict) and "messages" in prompt:
            messages = prompt["messages"]
            input_text = "\n".join(
                self.runtime._content_to_text(message.get("content"))
                for message in messages
                if message.get("content") is not None
            )
        else:
            input_text = str(prompt)

        return self.runtime.tts(
            model=self.model_name,
            input_text=input_text,
            params=filtered_params,
        )

    def _process_response(self, raw_response):
        return raw_response


class Codex(_OpenAIBaseModel):
    """OpenAI Codex wrapper using OAuth-backed responses transport."""

    def _do_api_call(self, prompt, **filtered_params):
        messages = prompt["messages"] if isinstance(prompt, dict) and "messages" in prompt else prompt
        return self.runtime.codex_responses(
            model=self.model_name,
            messages=messages,
            params=filtered_params,
        )

    def _process_response(self, raw_response):
        return raw_response

