import time
from openai import APIError, RateLimitError, APIConnectionError
from agentforge.utils.logger import Logger
import os
import base64


class UnsupportedModalityError(Exception):
    """Raised when a model doesn't support a requested modality."""
    pass


class BaseModel:
    """
    A base class encapsulating shared logic (e.g., logging, retries, prompt building).
    Subclasses must implement the _call_api method, which does the actual work of sending prompts.
    """

    # Defaults you might share across all models
    default_retries = 3
    default_backoff = 2

    supported_modalities = {"text"}

    def __init__(self, model_name, **kwargs):
        self.logger = None
        self.allowed_params = None
        self.excluded_params = None
        self.model_name = model_name
        self.num_retries = kwargs.get("num_retries", self.default_retries)
        self.base_backoff = kwargs.get("base_backoff", self.default_backoff)

    def generate(self, model_prompt=None, *, images=None, **params):
        """
        Main entry point for generating responses. This method handles retries,
        calls _call_api for the actual request, and logs everything.
        """
        self._validate_modalities(images)
        self._init_logger(model_prompt, params)

        parts        = self._build_parts(model_prompt, images)
        request_body = self._merge_parts(parts)

        return self._run_with_retries(request_body, params)

    # ─────────────────── helper trio for readability ────────────────────
    def _validate_modalities(self, images):
        if images and "image" not in self.supported_modalities:
            raise UnsupportedModalityError(f"{self.__class__.__name__} can't handle images")

    def _init_logger(self, model_prompt, params):
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        if model_prompt:
            self.logger.log_prompt(model_prompt)

    def _build_parts(self, model_prompt, images):
        parts = {"text": self._prepare_prompt(model_prompt)}
        if images:
            parts["image"] = self._prepare_image_payload(images)
        return parts

    # ─────────────────── retry/back‑off execution ───────────────────────
    def _run_with_retries(self, request_body, params):
        reply = None
        
        for attempt in range(self.num_retries):
            backoff = self.base_backoff ** (attempt + 1)
            
            try:
                filtered = self._prepare_params(**params)
                response = self._do_api_call(request_body, **filtered)
                reply    = self._process_response(response)

                self.logger.log_response(reply)
                break
            except RateLimitError as e:
                self.logger.warning(f"Rate limit exceeded: {e}. Retrying in {backoff} seconds...")
                time.sleep(backoff)
            except APIConnectionError as e:
                self.logger.warning(f"Connection error: {e}. Retrying in {backoff} seconds...")
                time.sleep(backoff)
            except APIError as e:
                if getattr(e, "status_code", None) == 502:
                    self.logger.warning(f"502 Bad Gateway. Retrying in {backoff} seconds...")
                    time.sleep(backoff)
                else:
                    raise
            except Exception as e:
                self.logger.warning(f"Error: {e}. Retrying in {backoff} seconds...")
                time.sleep(backoff)

        if reply is None:
            self.logger.critical("Error: All retries exhausted. No response received.")
            raise ValueError("Model generation failed: All retries exhausted. No response received.")
        
        # Validate that we received a non-empty response
        if not reply or (isinstance(reply, str) and not reply.strip()):
            self.logger.critical("Error: Model returned empty response.")
            raise ValueError("Model generation failed: Received empty response.")
            
        return reply

    def _prepare_image_payload(self, images):
        """Default implementation raises UnsupportedModalityError for image modality."""
        raise UnsupportedModalityError(f"{self.__class__.__name__} can't handle images")

    def _merge_parts(self, parts):
        """
        Combine text and optional image parts into an API-specific message format.
        Default implementation follows OpenAI-style format.
        """
        messages = parts["text"]
        if "image" in parts and parts["image"]:
            # If the last message is from the user, add images to it
            if messages and messages[-1]["role"] == "user":
                content = [{"type": "text", "text": messages[-1]["content"]}]
                content.extend(parts["image"])
                messages[-1]["content"] = content
            
        return {"messages": messages}

    @staticmethod
    def _prepare_prompt(model_prompt):
        # Format system/user messages in the appropriate style
        return [
            {"role": "system", "content": model_prompt.get('system')},
            {"role": "user", "content": model_prompt.get('user')}
        ]

    def _prepare_params(self, **params):
        if self.allowed_params:
            # Keep only parameters explicitly allowed
            return {k: v for k, v in params.items() if k in self.allowed_params}
        if self.excluded_params:
            # Exclude parameters listed in excluded_params
            return {k: v for k, v in params.items() if k not in self.excluded_params}
        # If neither allowed nor excluded parameters are defined, pass all params
        return params

    def _do_api_call(self, prompt, **filtered_params):
        # The actual request to the underlying client
        raise NotImplementedError("Subclasses must implement _do_call_api method.")

    def _process_response(self, raw_response):
        # Subclasses can process the raw responses as needed
        return raw_response
