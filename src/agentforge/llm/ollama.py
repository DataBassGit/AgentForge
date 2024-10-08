import requests
from agentforge.utils.Logger import Logger


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
            model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
            **params: Arbitrary keyword arguments for future extensibility, not used currently.

        Returns:
            str or None: The JSON response from the AI model if the request is successful, None otherwise.

        Logs the prompt and the response using a Logger instance. If the `CUSTOM_AI_ENDPOINT` environment variable
        is not set or if the request fails, appropriate error messages are logged.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        headers = {'Content-Type': 'application/json'}
        data = {
            "temperature": params["temperature"],
            "model": self._model,
            "system": model_prompt.get('System'),
            "prompt": model_prompt.get('User'),
            "max_tokens": params["max_new_tokens"],
            "stream": False
        }

        url = params.pop('host_url', None)
        if not url:
            self.logger.log(f"\n\nError: The CUSTOM_AI_ENDPOINT environment variable is not set: {url}", 'critical')

        response = requests.post(url, headers=headers, json=data)
        result = response.json()['choices'][0]['message']['content']
        self.logger.log_response(result)

        if response.status_code == 200:
            return result
        else:
            print(f"Request error: {response}")
            return None


# ----------------------------------------------------------------------------------------------------
# Example usage:
# prompt = "What does the cow say?"
# print(request_completion(prompt))
# print("Done!")
