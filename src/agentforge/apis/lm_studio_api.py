import requests
import json
from .base_api import BaseModel

class LMStudio(BaseModel):
    """
    Concrete implementation for OpenAI GPT models.
    """

    def _do_api_call(self, prompt, **filtered_params):
        url = filtered_params.pop('host_url', 'http://localhost:1234/v1/chat/completions')
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": self.model_name,
            "messages": prompt,
            **filtered_params
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # return error content
            self.logger.error(f"Request error: {response}")
            return None

        return response.json()

    def _process_response(self, raw_response):
        return raw_response["choices"][0]["message"]["content"]
