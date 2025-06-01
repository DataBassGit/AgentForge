import os
import time
import requests
from .base_api import BaseModel
from agentforge.utils.logger import Logger

# Get the API key from the environment variable
api_key = os.getenv('OPENROUTER_API_KEY')


class OpenRouter(BaseModel):
    """
    A class for interacting with OpenRouter's API to generate text based on provided prompts.

    Handles API calls to OpenRouter, including error handling and retries for failed requests.
    """


    def _do_api_call(self, prompt, **filtered_params):
        url = filtered_params.pop('host_url', 'https://openrouter.ai/api/v1/chat/completions')
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
            self.logger.error(f"Request error: {response}")
            return None

        return response.json()

    def _process_response(self, raw_response):
        # First, check if the response is empty
        if not raw_response:
            self.logger.error("Empty response received from API")
            return None

        # If there's an error in the response, log it and return an error message
        if 'error' in raw_response:
            error_code = raw_response['error'].get('code', 'unknown')
            error_message = raw_response['error'].get('message', 'No error message provided.')
            self.logger.error(f"API Error {error_code}: {error_message}")
            return f"Error {error_code}: {error_message}"

        # Otherwise, try to extract the content from the choices
        try:
            return raw_response['choices'][0]['message']['content']
        except (IndexError, KeyError) as e:
            self.logger.error(f"Unexpected response format: {e}")
            return None

