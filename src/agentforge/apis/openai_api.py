from .base_api import BaseModel
from openai import OpenAI
import io
from agentforge.apis.mixins.audio_input_mixin import AudioInputMixin
from agentforge.apis.mixins.audio_output_mixin import AudioOutputMixin

# Assuming you have set OPENAI_API_KEY in your environment variables
client = OpenAI()

class GPT(BaseModel):
    """
    Concrete implementation for OpenAI GPT models.
    """

    def _do_api_call(self, prompt, **filtered_params):
        if isinstance(prompt, dict) and "messages" in prompt:
            prompt = prompt["messages"]
        response = client.chat.completions.create(
            model=self.model_name,
            messages=prompt,
            **filtered_params
        )
        return response

    def _process_response(self, raw_response):
        return raw_response.choices[0].message.content

class O1Series(GPT):
    """
    Concrete implementation for OpenAI GPT models.
    """

    def _prepare_prompt(self, model_prompt):
        # Format user messages in the appropriate style
        content = f"{model_prompt.get('system', '')}\n\n{model_prompt.get('user', '')}"
        return [{"role": "user", "content": content}]

# ────────────────────────────────────────────────────────────────────────────
# Audio Wrappers
# ────────────────────────────────────────────────────────────────────────────

class STT(AudioInputMixin, BaseModel):
    """Speech-to-Text wrapper around OpenAI Whisper models."""

    def _merge_parts(self, parts, **params):
        """For STT we only care about the audio payload."""
        return {"audio": parts.get("audio")}

    def _do_api_call(self, prompt, **filtered_params):
        # `prompt` here is the dict returned by _merge_parts
        audio_blob = prompt.get("audio")
        if audio_blob is None:
            raise ValueError("STT generation called without audio data.")

        # Whisper endpoint expects a file-like object.
        if isinstance(audio_blob, (bytes, bytearray)):
            audio_file = io.BytesIO(audio_blob)
            audio_file.name = "audio.wav"  # OpenAI SDK requires a `name` attribute
        else:
            # assume path
            audio_file = open(audio_blob, "rb")

        try:
            response = client.audio.transcriptions.create(
                file=audio_file,
                model=self.model_name,
                **filtered_params
            )
        finally:
            # Close if we opened a real file on disk
            try:
                audio_file.close()
            except Exception:
                pass

        return response

    def _process_response(self, raw_response):
        # The OpenAI SDK returns an object with `.text`
        return getattr(raw_response, "text", str(raw_response))

class TTS(AudioOutputMixin, BaseModel):
    """Text-to-Speech wrapper producing audio bytes."""

    def _do_api_call(self, prompt, **filtered_params):
        # Convert prompt/messages → plain text input for TTS
        if isinstance(prompt, dict) and "messages" in prompt:
            messages = prompt["messages"]
            # Concatenate user/message content pieces
            input_text = "\n".join([m.get("content", "") for m in messages if m.get("content")])
        else:
            input_text = str(prompt)

        voice = filtered_params.pop("voice", "alloy")

        # OpenAI SDK ≥1.13 expects `response_format`; older versions used `format`.
        # Accept either key from upstream config for compatibility.
        audio_format = (
            filtered_params.pop("response_format", None)
            or filtered_params.pop("format", None)
            or "wav"
        )

        # Guarantee legacy key is not forwarded even if both are present.
        filtered_params.pop("format", None)

        response = client.audio.speech.create(
            model=self.model_name,
            voice=voice,
            input=input_text,
            response_format=audio_format,
            **filtered_params,
        )

        # SDK returns binary content in `.content`
        return getattr(response, "content", response)

    def _process_response(self, raw_response):
        # Simply return the bytes (pass-through)
        return raw_response

