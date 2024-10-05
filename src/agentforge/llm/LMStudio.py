import requests
import json
from agentforge.utils.Logger import Logger

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
            "model": self._model,
            "messages": [
                {"role": "system", "content": model_prompt.get('System')},
                {"role": "user", "content": model_prompt.get('User')}
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
