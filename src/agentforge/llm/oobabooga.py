# import sseclient  # pip install sseclient-py
import requests
from agentforge.utils.Logger import Logger


class Oobabooga:
    """
    A class for interacting with an external text generation service named Oobabooga. This class handles the
    construction and execution of requests to the Oobabooga API to generate text based on a given prompt.

    Attributes:
        _model (str): The model identifier used for generating text. This is kept for compatibility but may not
                      be directly used depending on the external service's API.
    """
    def __init__(self, model):
        """
        Initializes the Oobabooga class with a specific model identifier.

        Parameters:
            model (str): The identifier of the model to use for text generation.
        """
        self._model = model
        self.logger = None

    def generate_text(self, model_prompt, **params):
        """
        Generates text based on the provided prompt and additional parameters by making a request to the
        Oobabooga service's API.

        Parameters:
            model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
            **params: Arbitrary keyword arguments providing additional options for the request. This includes
                      'agent_name' for logging purposes and 'host_url' for specifying the Oobabooga service's address.

        Returns:
            str: The generated text from the Oobabooga service.

        Raises:
            Exception: Logs a critical error message if an exception occurs during the API request.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        prompt = '\n\n'.join(model_prompt)

        # Server address
        host = params.pop('host_url', None)
        url = f"{host}/v1/chat/completions"

        headers = {"Content-Type": "application/json"}

        message = [{"role": "user", "content": prompt}]

        data = {
            "mode": "chat",
            "character": "Example",
            "messages": message
        }

        reply = ''
        try:
            response = requests.post(url, headers=headers, json=data, verify=False)

            reply = response.json()['choices'][0]['message']['content']
            self.logger.log_response(reply)


        except Exception as e:
            self.logger.log(f"\n\nError: {e}", 'critical')

        return reply
