import os
import time
import requests
from .base_api import BaseModel
from agentforge.utils.logger import Logger

# Get the API key from the environment variable
api_key = os.getenv('AKASH_API_KEY')


class Akash(BaseModel):
    """
    A class for interacting with Akash's API to generate text based on provided prompts.

    Handles API calls to OpenRouter, including error handling and retries for failed requests.
    """


    def _do_api_call(self, prompt, **filtered_params):
        url = filtered_params.pop('host_url', 'https://chatapi.akash.network/api/v1')
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": filtered_params.pop("http_referer", ""),
            "X-Title": 'AgentForge'
        }
        data = {
            "model": self.model_name,
            "messages": prompt,
            **filtered_params
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # return error content
            self.logger.log(f"Request error: {response}", 'error')
            return None

        return response.json()

    def _process_response(self, raw_response):
        return raw_response['choices'][0]['message']['content']
