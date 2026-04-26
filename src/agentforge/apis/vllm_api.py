import requests
import json
from .base_api import BaseModel


class VLLM(BaseModel):
    """
    Implementation for vLLM hosted models via OpenAI-compatible API.
    """

    def _do_api_call(self, prompt, **filtered_params):
        # Extract messages from prompt dict if needed
        if isinstance(prompt, dict) and "messages" in prompt:
            prompt = prompt["messages"]

        # Get the host URL, defaulting to vLLM's standard endpoint
        url = filtered_params.pop('host_url', 'http://localhost:8000/v1/chat/completions')

        # Get optional API key
        api_key = filtered_params.pop('api_key', None)

        # Set up headers
        headers = {'Content-Type': 'application/json'}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        # vLLM-specific parameters that aren't in OpenAI API
        # Extract them to extra_body if present
        extra_params = {}
        vllm_specific = ['top_k', 'repetition_penalty', 'length_penalty',
                         'min_tokens', 'guided_choice', 'guided_json',
                         'guided_regex', 'guided_grammar']

        for param in vllm_specific:
            if param in filtered_params:
                extra_params[param] = filtered_params.pop(param)

        # Build the request payload
        data = {
            "model": self.model_name,
            "messages": prompt,
            **filtered_params
        }

        # Add vLLM-specific params if any exist
        if extra_params:
            data['extra_body'] = extra_params

        # Make the API call
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            self.logger.error(f"Request error: {response.status_code} - {response.text}")
            return None

        return response.json()

    def _process_response(self, raw_response):
        """Extract the content from vLLM's OpenAI-compatible response."""
        return raw_response["choices"][0]["message"]["content"]
