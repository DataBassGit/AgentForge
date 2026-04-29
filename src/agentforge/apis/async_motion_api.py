import httpx
import asyncio
from typing import Optional, Dict, Any
from .async_base_api import AsyncBaseModel

# Default port for the local motion_server.py
DEFAULT_MGM_URL = "http://localhost:5005"


class MGMAsyncRuntime:
    """
    Handles the asynchronous HTTP communication with the local MG-MotionLLM server.
    """

    def __init__(self, base_url: str = DEFAULT_MGM_URL):
        self.base_url = base_url.rstrip("/")
        # Motion generation is typically sub-100ms, but we set a reasonable timeout
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=30.0))

    async def generate_motion(self, text: str, logger=None) -> Dict[str, Any]:
        """
        Sends the motion description to the local MG-MotionLLM server.
        Expects a JSON response containing the 13-point OSC tracking data or metadata.
        """
        url = f"{self.base_url}/generate"
        payload = {"text": text}

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            if logger:
                logger.error(f"MGM Motion API Error: {e}")
            raise

    async def close(self):
        await self.client.aclose()


class AsyncMotionSmall(AsyncBaseModel):
    """
    AgentForge API integration for the MG-MotionLLM (Small) engine.
    This class bridges the 'Brain' (LLM) to the 'Body' (VRChat/OSC).
    """

    def __init__(self, model_name="mg-motion-small", **kwargs):
        super().__init__(model_name, **kwargs)
        # Use provided base_url from kwargs or fall back to default
        base_url = kwargs.get("base_url", DEFAULT_MGM_URL)
        self.runtime = MGMAsyncRuntime(base_url=base_url)

    def _prepare_params(self, **kwargs):
        """
        Passes parameters directly to the runtime without filtering.
        """
        return kwargs

    def _build_parts(self, model_prompt, images, audio):
        """
        Extracts the action/motion text safely from the prompt.
        """
        if isinstance(model_prompt, dict):
            # AgentForge standard: pull from 'user' or 'system' keys
            text = model_prompt.get("user", "") or model_prompt.get("system", "")
        else:
            text = str(model_prompt)

        return {"text": text}

    def _merge_parts(self, parts):
        """
        Passes the extracted text dictionary through to the call method.
        """
        return parts

    async def _do_api_call_async(self, request_body, **filtered_params):
        """
        Executes the async call to the motion server.
        """
        text = request_body.get("text", "") if isinstance(request_body, dict) else str(request_body)

        if not text:
            return {"status": "skipped", "message": "No motion text provided"}

        return await self.runtime.generate_motion(
            text=text,
            logger=self.logger
        )

    def _process_response(self, raw_response):
        """
        Processes the JSON response from the motion server.
        """
        # Typically returns the OSC point list or a success confirmation for the buffer
        return raw_response