import os
from .base_api import BaseModel, ModelResponseError, NonRetriableModelError
from groq import Groq


class GroqAPI(BaseModel):
    def _do_api_call(self, prompt, **filtered_params):
        messages = prompt["messages"] if isinstance(prompt, dict) and "messages" in prompt else prompt
        request_params = dict(filtered_params)
        if "max_completion_tokens" not in request_params and "max_tokens" in request_params:
            request_params["max_completion_tokens"] = request_params.pop("max_tokens")
        else:
            request_params.pop("max_tokens", None)

        response = self._get_client().chat.completions.create(
            model=self.model_name, messages=messages, **request_params
        )
        return response

    @staticmethod
    def _get_client():
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise NonRetriableModelError("GROQ_API_KEY is not set. Export GROQ_API_KEY before using Groq models.")
        return Groq(api_key=api_key)

    def _process_response(self, raw_response):
        try:
            content = raw_response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise ModelResponseError(f"GroqAPI received a malformed response for model '{self.model_name}'.") from exc

        if not isinstance(content, str) or not content.strip():
            raise ModelResponseError(f"GroqAPI received an empty response for model '{self.model_name}'.")
        return content
