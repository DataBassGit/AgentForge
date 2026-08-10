import os
import anthropic
from .base_api import BaseModel, ModelResponseError, NonRetriableModelError


class Claude(BaseModel):
    """
    A class for interacting with Anthropic's Claude models to generate text based on provided prompts.

    Manages API calls to Anthropic, handling errors such as rate limits, and retries failed requests with exponential
    backoff.
    """

    @staticmethod
    def _prepare_prompt(model_prompt):
        """Build payload parts in Anthropic-expected shape.

        Anthropic expects:
            {
              "system":   "<system string>",   # optional
              "messages": [
                  {"role": "user", "content": "..."}
              ]
            }
        We purposely keep `system` separate (not as a message role) so that
        the top-level `system` parameter can be forwarded untouched by
        `_merge_parts()` / `_do_api_call()`.
        """

        return {
            "messages": [{"role": "user", "content": model_prompt.get("user")}],
            "system": model_prompt.get("system"),
        }

    # ------------------------------------------------------------------
    # Anthropic-specific overrides of BaseModel helpers
    # ------------------------------------------------------------------

    def _merge_parts(self, parts):
        """Return the text part verbatim.

        BaseModel's default implementation would nest the payload under an
        extra "messages" key. We override it so the dictionary produced by
        `_prepare_prompt()` is passed through unchanged.
        """

        # We ignore image parts for now – Claude Vision support could be added
        # later with a dedicated modality handler.
        return parts["text"]

    def _do_api_call(self, prompt, **filtered_params):
        """Send the request to Anthropic with correctly separated params."""

        return self._get_client().messages.create(
            model=self.model_name, messages=prompt["messages"], system=prompt.get("system"), **filtered_params
        )

    @staticmethod
    def _get_client():
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise NonRetriableModelError(
                "ANTHROPIC_API_KEY is not set. Export ANTHROPIC_API_KEY before using Anthropic models."
            )
        return anthropic.Anthropic(api_key=api_key)

    def _process_response(self, raw_response):
        try:
            first_content = raw_response.content[0]
        except (AttributeError, IndexError, TypeError) as exc:
            raise ModelResponseError(f"Claude received a malformed response for model '{self.model_name}'.") from exc

        text = first_content.get("text") if isinstance(first_content, dict) else getattr(first_content, "text", None)
        if not isinstance(text, str) or not text.strip():
            raise ModelResponseError(f"Claude received an empty response for model '{self.model_name}'.")
        return text
