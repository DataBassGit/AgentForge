import asyncio
import time
from httpx import HTTPStatusError, RequestError
from agentforge.utils.logger import Logger
from .base_api import BaseModel, UnsupportedModalityError, NonRetriableModelError


class AsyncBaseModel(BaseModel):
    """
    An asynchronous version of the BaseModel.
    Designed for non-blocking I/O and parallel execution.
    """

    async def generate_async(self, model_prompt=None, *, images=None, audio=None, **params):
        """
        Asynchronous entry point for generating responses.
        """
        if images is None and "images" in params:
            images = params.pop("images")
        if audio is None and "audio" in params:
            audio = params.pop("audio")

        self._validate_modalities(images, audio)

        # Initialize logger (sync)
        self._init_logger(model_prompt, params)

        parts = self._build_parts(model_prompt, images, audio)
        request_body = self._merge_parts(parts)

        return await self._run_with_retries_async(request_body, params)

    async def _run_with_retries_async(self, request_body, params):
        reply = None

        for attempt in range(self.num_retries):
            backoff = self.base_backoff ** (attempt + 1)

            try:
                filtered = self._prepare_params(**params)
                # Call the async version of the API call
                response = await self._do_api_call_async(request_body, **filtered)
                reply = self._process_response(response)

                if isinstance(reply, (bytes, bytearray)):
                    self.logger.log_response(f"<binary {len(reply)} bytes>")
                else:
                    self.logger.log_response(reply)
                break

            except (HTTPStatusError, RequestError) as e:
                # Handle status errors (like 429 or 502) and connection issues
                status_code = getattr(e.response, "status_code", None) if hasattr(e, "response") else None

                if status_code in [429, 502, 503, 504] or isinstance(e, RequestError):
                    self.logger.warning(f"Transient error ({type(e).__name__}): {e}. Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                else:
                    raise
            except Exception as e:
                self.logger.warning(f"Unexpected error: {e}. Retrying in {backoff} seconds...")
                await asyncio.sleep(backoff)

        if reply is None:
            self.logger.critical("Error: All retries exhausted.")
            raise ValueError("Async generation failed: All retries exhausted.")

        return reply

    async def _do_api_call_async(self, prompt, **filtered_params):
        """Subclasses must implement this async method."""
        raise NotImplementedError("Subclasses must implement _do_api_call_async.")