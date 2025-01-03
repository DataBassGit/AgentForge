import os
import time
import requests
from .BaseAPI import BaseModel
from agentforge.utils.Logger import Logger

# Get the API key from the environment variable
api_key = os.getenv('OPENROUTER_API_KEY')


class OpenRouter(BaseModel):
    """
    A class for interacting with OpenRouter's API to generate text based on provided prompts.

    Handles API calls to OpenRouter, including error handling and retries for failed requests.
    """


    def _do_api_call(self, prompt, **filtered_params):
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": filtered_params.get("http_referer", ""),
            "X-Title": 'AgentForge'
        }

        data = {
            "model": self.model_name,
            "messages": prompt,
            **filtered_params
        }

        url = filtered_params.pop('host_url', 'https://openrouter.ai/api/v1/chat/completions')
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # return error content
            self.logger.log(f"Request error: {response}", 'error')
            return None

        return response.json()

    def _process_response(self, raw_response):
        return raw_response['choices'][0]['message']['content']

    # def generate_text(self, model_prompt, **params):
    #     """
    #     Generates text based on the provided prompts and additional parameters for the OpenRouter model.
    #
    #     Parameters:
    #         model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
    #         **params: Arbitrary keyword arguments providing additional options to the model and API call.
    #
    #     Returns:
    #         str or None: The generated text from the OpenRouter model or None if the operation fails.
    #     """
    #     self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
    #     self.logger.log_prompt(model_prompt)
    #
    #     prompt = [
    #         {"role": "system", "content": model_prompt.get('System')},
    #         {"role": "user", "content": model_prompt.get('User')}
    #     ]
    #
    #     headers = {
    #         "Authorization": f"Bearer {api_key}",
    #         "Content-Type": "application/json",
    #         "HTTP-Referer": params.get("http_referer", ""),
    #         "X-Title": 'AgentForge'
    #     }
    #
    #     data = {
    #         "model": self._model,
    #         "messages": prompt,
    #         "max_tokens": params.get("max_new_tokens"),
    #         "temperature": params.get("temperature"),
    #         "top_p": params.get("top_p"),
    #         "presence_penalty": params.get("penalty_alpha"),
    #         "stop": params.get("stop"),
    #         "stream": params.get("stream", False)
    #     }
    #
    #     reply = None
    #     for attempt in range(self.num_retries):
    #         backoff = 2 ** (attempt + 2)
    #         try:
    #             response = requests.post(
    #                 "https://openrouter.ai/api/v1/chat/completions",
    #                 headers=headers,
    #                 json=data
    #             )
    #             response.raise_for_status()
    #             reply = response.json()['choices'][0]['message']['content']
    #             self.logger.log_response(reply)
    #             break
    #
    #         except requests.exceptions.RequestException as e:
    #             error_message = f"\n\nError: {str(e)}"
    #             try:
    #                 error_message += f"\nResponse JSON: {response.json()}"
    #             except ValueError:
    #                 error_message += "\nUnable to parse response JSON"
    #
    #             if response.status_code == 429:  # Rate limit error
    #                 self.logger.log(error_message + f", retrying in {backoff} seconds...", 'warning')
    #             elif response.status_code == 502:  # Bad gateway
    #                 self.logger.log(error_message + f", retrying in {backoff} seconds...", 'warning')
    #             else:
    #                 self.logger.log(error_message + f", retrying in {backoff} seconds...", 'warning')
    #             time.sleep(backoff)
    #
    #     if reply is None:
    #         self.logger.log("\n\nError: Failed to get OpenRouter Response", 'critical')
    #
    #     return reply
