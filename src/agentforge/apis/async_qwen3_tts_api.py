import httpx
import asyncio
from typing import Optional
from .async_base_api import AsyncBaseModel

# Port updated back to 8100 to hit the unified server
QWEN3_TTS_BASE_URL = "http://localhost:8100"


class Qwen3TTSAsyncRuntime:
    """
    Handles the asynchronous HTTP communication with the local Qwen3-TTS server.
    """

    def __init__(self, base_url: str = QWEN3_TTS_BASE_URL):
        self.base_url = base_url.rstrip("/")
        # TTS generation can take a moment depending on the text length and hardware
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=120.0))

    async def tts(self, text: str, instruction: str, params: dict, logger=None) -> bytes:
        """
        Sends the text and the voice design instruction to the TTS server.
        Expects a raw audio byte stream (e.g., WAV format) in return.
        """
        url = f"{self.base_url}/v1/audio/speech"

        payload = {
            "input": text,
            "instruction": instruction,
            **params
        }

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            # For TTS, we return the raw binary content (the audio file)
            return response.content

        except Exception as e:
            if logger:
                logger.error(f"TTS API Error: {e}")
            raise

    async def close(self):
        await self.client.aclose()


class AsyncQwen3TTS(AsyncBaseModel):
    """
    AgentForge API integration for Qwen3-TTS Voice Design.
    """

    def __init__(self, model_name="qwen3-tts-1.7b-voicedesign", **kwargs):
        super().__init__(model_name, **kwargs)
        base_url = kwargs.get("base_url", QWEN3_TTS_BASE_URL)
        self.runtime = Qwen3TTSAsyncRuntime(base_url=base_url)

    def _prepare_params(self, **kwargs):
        """
        CRITICAL FIX: Overrides AgentForge's default param stripper.
        Ensures 'instruction', 'speaker', and 'language' are passed to the server.
        """
        return kwargs

    def _build_parts(self, model_prompt, images, audio):
        """
        Extracts the text prompt for the TTS engine safely.
        """
        # Since AgentForge forces us to pass a dict to bypass the logger crash,
        # we must unpack it here so Qwen doesn't speak the JSON syntax out loud!
        if isinstance(model_prompt, dict):
            text = model_prompt.get("user", "") or model_prompt.get("system", "")
        else:
            text = str(model_prompt)

        return {"text": text}

    def _merge_parts(self, parts):
        """
        Returns the dictionary so AgentForge's BaseModel doesn't crash on .get()
        """
        return parts

    async def _do_api_call_async(self, request_body, **filtered_params):
        """
        Executes the async API call. Separates the text input from the
        paralinguistic instructions (voice design).
        """
        # Safely handle the dictionary returned by _merge_parts
        text = request_body.get("text", "") if isinstance(request_body, dict) else str(request_body)

        if not text:
            return b""

        # Extract the instruction if provided in the params (e.g., "A female speaking with a sudden, bright laugh")
        instruction = filtered_params.pop("instruction", "")

        return await self.runtime.tts(
            text=text,
            instruction=instruction,
            params=filtered_params,
            logger=self.logger
        )

    def _process_response(self, raw_response):
        """
        Processes the returned data. Since it's audio, we just pass the bytes through.
        The AsyncBaseModel will intelligently log `<binary X bytes>` instead of crashing.
        """
        return raw_response