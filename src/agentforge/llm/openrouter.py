import os
import time
import requests
from agentforge.utils.functions.Logger import Logger

# Get the API key from the environment variable
api_key = os.getenv('OPENROUTER_API_KEY')


class OpenRouter:
    """
    A class for interacting with OpenRouter's API to generate text based on provided prompts.

    Handles API calls to OpenRouter, including error handling and retries for failed requests.

    Attributes:
        num_retries (int): The number of times to retry generating text upon encountering errors.
    """
    num_retries = 5

    def __init__(self, model):
        """
        Initializes the OpenRouter class with a specific model.

        Parameters:
            model (str): The identifier of the model to use for generating text.
        """
        self._model = model
        self.logger = None

    def generate_text(self, model_prompt, **params):
        """
        Generates text based on the provided prompts and additional parameters for the OpenRouter model.

        Parameters:
            model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
            **params: Arbitrary keyword arguments providing additional options to the model and API call.

        Returns:
            str or None: The generated text from the OpenRouter model or None if the operation fails.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        prompt = [
            {"role": "system", "content": model_prompt.get('System')},
            {"role": "user", "content": model_prompt.get('User')}
        ]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": params.get("http_referer", ""),
            "X-Title": 'AgentForge'
        }

        data = {
            "model": self._model,
            "messages": prompt,
            "max_tokens": params.get("max_new_tokens"),
            "temperature": params.get("temperature"),
            "top_p": params.get("top_p"),
            "presence_penalty": params.get("penalty_alpha"),
            "stop": params.get("stop"),
            "stream": params.get("stream", False)
        }

        reply = None
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                reply = response.json()['choices'][0]['message']['content']
                self.logger.log_response(reply)
                break

            except requests.exceptions.RequestException as e:
                error_message = f"\n\nError: {str(e)}"
                try:
                    error_message += f"\nResponse JSON: {response.json()}"
                except ValueError:
                    error_message += "\nUnable to parse response JSON"
                
                if response.status_code == 429:  # Rate limit error
                    self.logger.log(error_message + f", retrying in {backoff} seconds...", 'warning')
                elif response.status_code == 502:  # Bad gateway
                    self.logger.log(error_message + f", retrying in {backoff} seconds...", 'warning')
                else:
                    self.logger.log(error_message + f", retrying in {backoff} seconds...", 'warning')
                time.sleep(backoff)

        if reply is None:
            self.logger.log("\n\nError: Failed to get OpenRouter Response", 'critical')

        return reply
