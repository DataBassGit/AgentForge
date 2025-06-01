import requests
import json
from .base_api import BaseModel

class Ollama(BaseModel):

    @staticmethod
    def _prepare_prompt(model_prompt):
        return model_prompt

    def _do_api_call(self, prompt, **filtered_params):
        url = filtered_params.pop('host_url', 'http://localhost:11434/api/generate')
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": self.model_name,
            "system": prompt.get('system'),
            "prompt": prompt.get('user'),
            **filtered_params
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # return error content
            self.logger.error(f"Request error: {response}")
            return None

        return response.json()

    def _process_response(self, raw_response):
        # Handle different Ollama endpoint responses
        if raw_response is None:
            return None
        if 'response' in raw_response:  # /api/generate
            return raw_response['response']
        elif 'message' in raw_response:  # /api/chat
            return raw_response['message']['content']
        elif 'choices' in raw_response:
            return raw_response['choices'][0]['message']['content']
        else:
            self.logger.error(f"Unexpected Ollama response format: {raw_response}")
            return None
