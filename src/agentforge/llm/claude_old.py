import os
import time
import anthropic
from agentforge.utils.functions.Logger import Logger

API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=API_KEY)


def parse_prompts(prompts):
    """
    Formats a list of prompts into a single string formatted specifically for Anthropic's AI models.

    Parameters:
        prompts (list): A list of strings, each representing a segment of the overall prompt.

    Returns:
        str: A formatted prompt string combining human and AI prompt indicators with the original prompt content.
    """
    prompt = ''.join(prompts[0:])
    prompt = f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}"

    return prompt


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

    def generate_text(self, prompts, **params):
        """
        Generates text based on the provided prompts and additional parameters for the Claude model.

        Parameters:
            prompts (list): A list of strings to be passed as prompts to the Claude model.
            **params: Arbitrary keyword arguments providing additional options to the model such as
                      'max_new_tokens', 'temperature', and 'top_p'.

        Returns:
            str or None: The generated text from the model or None if the operation fails after retry attempts.

        This method attempts to generate content with the provided prompts and configuration, retrying up to a
        specified number of times with exponential backoff in case of errors. It logs the process and outcomes.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        prompt = parse_prompts(prompts)
        self.logger.log_prompt(prompt)

        # Will retry to get chat if a rate limit or bad gateway error is received from the chat
        response = None
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = client.completions.create(
                    prompt=prompt,
                    # stop_sequences=[anthropic.HUMAN_PROMPT],
                    model=self._model,
                    max_tokens_to_sample=params["max_new_tokens"],
                    temperature=params["temperature"],
                    top_p=params["top_p"]
                )
                # print(f"Response:{response}\n")
                self.logger.log_response(response.completion)
                break

            except Exception as e:
                self.logger.log(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}", 'warning')
                time.sleep(backoff)

        if response is None:
            self.logger.log("\n\nError: Failed to get Anthropic Response", 'critical')

        return response.completion
