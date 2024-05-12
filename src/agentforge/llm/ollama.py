import requests
import json
from agentforge.utils.functions.Logger import Logger


def parse_prompts(prompts):
    """
    Formats a list of prompts into a single string formatted specifically for Anthropic's AI models.

    Parameters:
        prompts (list): A list of strings, each representing a segment of the overall prompt.

    Returns:
        str: A formatted prompt string combining human and AI prompt indicators with the original prompt content.
    """
    prompt = ''.join(prompts[1:])

    return prompt


class Ollama:

    def __init__(self, model):
        """
        Initializes the CustomAPI class.
        """
        self._model = model
        self.logger = None

    def generate_text(self, model_prompt, **params):
        """
        Sends a request to a custom AI model endpoint to generate a completion based on the provided prompt.

        This function constructs a request with specified parameters and sends it to a custom AI endpoint, which is
        expected to generate text based on the input prompt. The endpoint URL is read from an environment variable.

        Parameters:
            model_prompt (list): The prompt text to send to the model for generating a completion.
            **params: Arbitrary keyword arguments for future extensibility, not used currently.

        Returns:
            str or None: The JSON response from the AI model if the request is successful, None otherwise.

        Logs the prompt and the response using a Logger instance. If the `CUSTOM_AI_ENDPOINT` environment variable
        is not set or if the request fails, appropriate error messages are logged.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        prompt = parse_prompts(model_prompt)
        self.logger.log_prompt(prompt)

        headers = {'Content-Type': 'application/json'}
        data = {
            "temperature": params["temperature"],
            "model": self._model,
            "system": model_prompt[0],
            "prompt": prompt,
            "max_tokens": params["max_new_tokens"],
            "stream": False
        }

        url = params.pop('host_url', None)
        if not url:
            self.logger.log("\n\nError: The CUSTOM_AI_ENDPOINT environment variable is not set", 'critical')

        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.logger.log_response(response.json()['response'])

        if response.status_code == 200:
            return response.json()['response']
        else:
            print(f"Request error: {response}")
            return None


# ----------------------------------------------------------------------------------------------------
# Example usage:
# prompt = "What does the cow say?"
# print(request_completion(prompt))
# print("Done!")
