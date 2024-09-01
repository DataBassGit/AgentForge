import os
import time
import requests
from agentforge.utils.functions.Logger import Logger

# Get the API key from the environment variable
api_key = os.getenv('OPENROUTER_API_KEY')

def parse_prompts(prompts):
    """
    Transforms a list of prompt segments into a structured format expected by the OpenRouter chat interface.

    Parameters: prompts (list): A list where the first element is considered the 'system' prompt and the rest are
    'user' prompts.

    Returns:
        list: A list of dictionaries, each representing a part of the conversation with roles ('system' or 'user')
        and their content.
    """
    return [
        {"role": "system", "content": prompts[0]},
        {"role": "user", "content": "".join(prompts[1:])}
    ]

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

    def generate_text(self, prompts, **params):
        """
        Generates text based on the provided prompts and additional parameters for the OpenRouter model.

        Parameters:
            prompts (list): A list of strings to be passed as prompts to the OpenRouter model.
            **params: Arbitrary keyword arguments providing additional options to the model and API call.

        Returns:
            str or None: The generated text from the OpenRouter model or None if the operation fails.
        """
        self.logger = Logger(name=params.pop('agent_name', None))
        self.logger.log_prompt(''.join(prompts))

        messages = parse_prompts(prompts)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": params.get("http_referer", ""),
            "X-Title": 'AgentForge'
        }

        data = {
            "model": self._model,
            "messages": messages,
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
                if response.status_code == 429:  # Rate limit error
                    self.logger.log("\n\nError: Reached API rate limit, retrying in 20 seconds...", 'warning')
                    time.sleep(20)
                elif response.status_code == 502:  # Bad gateway
                    self.logger.log("\n\nError: Connection issue, retrying in 2 seconds...", 'warning')
                    time.sleep(backoff)
                else:
                    self.logger.log(f"\n\nError: {str(e)}, retrying in {backoff} seconds...", 'warning')
                    time.sleep(backoff)

        if reply is None:
            self.logger.log("\n\nError: Failed to get OpenRouter Response", 'critical')

        return reply
