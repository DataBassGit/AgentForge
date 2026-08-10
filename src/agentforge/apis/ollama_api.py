import requests
from .base_api import BaseModel, ModelResponseError


class Ollama(BaseModel):
    @staticmethod
    def _prepare_prompt(model_prompt):
        return model_prompt

    def _merge_parts(self, parts):
        """Return prompts in the system/user shape expected by Ollama."""
        return parts["text"]

    def _do_api_call(self, prompt, **filtered_params):
        url = filtered_params.pop("host_url", "http://localhost:11434/api/generate")
        headers = {"Content-Type": "application/json"}
        request_params = self._prepare_request_params(filtered_params)
        data = {
            "model": self.model_name,
            "system": prompt.get("system"),
            "prompt": prompt.get("user"),
            **request_params,
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            body_excerpt = (response.text or "").strip().replace("\n", " ")[:200]
            raise ModelResponseError(
                f"Ollama request for model '{self.model_name}' failed with HTTP {response.status_code}. "
                f"Response excerpt: {body_excerpt}"
            )

        return response.json()

    @staticmethod
    def _prepare_request_params(params):
        request_params = dict(params)
        if "num_predict" not in request_params and "max_tokens" in request_params:
            request_params["num_predict"] = request_params.pop("max_tokens")
        else:
            request_params.pop("max_tokens", None)

        options = {}
        option_names = {"num_predict", "temperature", "top_p", "top_k", "repeat_penalty", "seed", "stop"}
        for name in option_names:
            if name in request_params:
                options[name] = request_params.pop(name)

        if options:
            request_params["options"] = options
        return request_params

    def _process_response(self, raw_response):
        # Handle different Ollama endpoint responses
        if raw_response is None:
            raise ModelResponseError(f"Ollama received an empty response for model '{self.model_name}'.")
        if "response" in raw_response:  # /api/generate
            return raw_response["response"]
        elif "message" in raw_response:  # /api/chat
            return raw_response["message"]["content"]
        elif "choices" in raw_response:
            return self._extract_chat_choice_content(raw_response)
        else:
            raise ModelResponseError(f"Ollama received a malformed response for model '{self.model_name}'.")
