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
        return {
            'messages': [{'role': 'user', 'content': model_prompt.get('user')}],
            'system': model_prompt.get('system')
        }

    def _do_api_call(self, prompt, **filtered_params):
        response = client.messages.create(
            model=self.model_name,
            messages=prompt.get('messages'),
            system=prompt.get('system'),
            **filtered_params
        )
        return response

    def _process_response(self, raw_response):
        return raw_response.content[0].text