import os
import time
import anthropic
from agentforge.utils.Logger import Logger

API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=API_KEY)


class Claude:
    """
    A class for interacting with Anthropic's Claude models to generate text based on provided prompts.

    Manages API calls to Anthropic, handling errors such as rate limits, and retries failed requests with exponential
    backoff.

    Attributes:
        num_retries (int): The number of times to retry generating text upon encountering errors.
    """
    num_retries = 5

    def __init__(self, model):
        """
        Initializes the Claude class with a specific Claude model identifier.

        Parameters:
            model (str): The identifier of the Claude model to use for generating text.
        """
        self._model = model
        self.logger = None

    def generate_text(self, model_prompt, **params):
        """
        Generates text based on the provided prompts and additional parameters for the Claude model.

        Parameters:
            model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
            **params: Arbitrary keyword arguments providing additional options to the model such as
                      'max_new_tokens', 'temperature', and 'top_p'.

        Returns:
            str or None: The generated text from the model or None if the operation fails after retry attempts.

        This method attempts to generate content with the provided prompts and configuration, retrying up to a
        specified number of times with exponential backoff in case of errors. It logs the process and outcomes.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        prompt = [{'role': 'user', 'content': model_prompt.get('User')}]

        # Will retry to get chat if a rate limit or bad gateway error is received from the chat
        response = None
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = client.messages.create(
                    messages=prompt,
                    system=model_prompt.get('System'),
                    # stop_sequences=[anthropic.HUMAN_PROMPT],
                    model=self._model,
                    max_tokens=params["max_new_tokens"],
                    temperature=params["temperature"],
                    top_p=params["top_p"]
                )
                self.logger.log_response(str(response.content[0].text))
                break

            except Exception as e:
                self.logger.log(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}", 'warning')
                time.sleep(backoff)

        if response is None:
            self.logger.log("\n\nError: Failed to get Anthropic Response", 'critical')
        else:
            usage = str(response.usage)
            self.logger.log(f"Claude Token Usage: {usage}\n", 'debug')

        return response.content[0].text
