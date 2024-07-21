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


class LMStudio:

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
        self.logger.log(f'System Prompt:\n{model_prompt[0]}', 'debug', 'ModelIO')
        self.logger.log(f'User Prompt:\n{prompt}', 'debug', 'ModelIO')
        # self.logger.log_prompt(prompt)

        headers = {'Content-Type': 'application/json'}
        data = {
            "temperature": 0.8,
            "model": self._model,
            "system": model_prompt[0],
            "prompt": prompt,
            "max_tokens": 2048,
            "stream": False
        }
        data = {
            "model": self._model,
            "messages": [
              {"role": "system", "content": model_prompt[0]},
              {"role": "user", "content": prompt}
            ],
            "temperature": params["temperature"],
            "max_tokens": params["max_new_tokens"],
            "stream": False
        }

        url = params.pop('host_url', None)
        if not url:
            self.logger.log("\n\nError: The CUSTOM_AI_ENDPOINT environment variable is not set", 'critical')

        completion = requests.post(url, headers=headers, data=json.dumps(data))
        response_dict = json.loads(completion.text)
        message_content = response_dict["choices"][0]["message"]["content"]

        # self.logger.log_response(response.json()['response'])
        self.logger.log_response(message_content)

        if completion.status_code == 200:
            return message_content
        else:
            print(f"Request error: {completion}")
            return None


# ----------------------------------------------------------------------------------------------------
# Example usage:
# prompt = "What does the cow say?"
# print(request_completion(prompt))
# print("Done!")
