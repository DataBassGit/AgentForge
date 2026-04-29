import httpx
import asyncio
from .async_base_api import AsyncBaseModel
from agentforge.apis.mixins.audio_input_mixin import AudioInputMixin

BUDE_WHISPER_BASE_URL = "http://localhost:8100"


class BudeWhisperAsyncRuntime:
    def __init__(self, base_url: str = BUDE_WHISPER_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(60.0, read=120.0))

    async def stt(self, model: str, audio_blob: bytes, params: dict, logger=None) -> str:
        url = f"{self.base_url}/v1/audio/transcriptions"
        files = {"file": ("audio.wav", audio_blob, "audio/wav")}
        data = {"model": model, **params}

        try:
            response = await self.client.post(url, files=files, data=data)
            response.raise_for_status()
            result = response.json()

            # PARSING NEW DUAL RESPONSE
            # Returns: "[Caption] Transcription"
            caption = result.get("caption", "").strip()
            text = result.get("transcription", "").strip()

            if caption and text:
                return f"[{caption}] {text}"
            return text or caption or "[No transcription or caption generated]"

        except Exception as e:
            if logger: logger.error(f"STT API Error: {e}")
            raise

    async def close(self):
        await self.client.aclose()


class AsyncSTT(AudioInputMixin, AsyncBaseModel):
    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)
        base_url = kwargs.get("base_url", BUDE_WHISPER_BASE_URL)
        self.runtime = BudeWhisperAsyncRuntime(base_url=base_url)

    def _build_parts(self, model_prompt, images, audio):
        parts = {}
        if audio: parts["audio"] = self._prepare_audio_payload(audio)
        return parts

    def _merge_parts(self, parts):
        return {"audio": parts.get("audio")}

    async def _do_api_call_async(self, prompt, **filtered_params):
        audio_blob = prompt.get("audio")
        if not audio_blob: return ""

        return await self.runtime.stt(
            model=self.model_name,
            audio_blob=audio_blob,
            params=filtered_params,
            logger=self.logger
        )

    def _process_response(self, raw_response):
        processed = str(raw_response) if raw_response is not None else ""
        if self.logger: self.logger.log_response(processed)
        return processed