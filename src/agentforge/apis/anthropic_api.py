import os
import anthropic
from .base_api import BaseModel

API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=API_KEY)


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

        return client.messages.create(
            model=self.model_name,
            messages=prompt["messages"],
            system=prompt.get("system"),
            **filtered_params,
        )

    def _process_response(self, raw_response):
        return raw_response.content[0].text