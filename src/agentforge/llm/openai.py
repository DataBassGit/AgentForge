import time
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from agentforge.utils.Logger import Logger

# Assuming you have set OPENAI_API_KEY in your environment variables
client = OpenAI()


class GPT:
    """
    A class for interacting with OpenAI's GPT models to generate text based on provided prompts.

    Handles API calls to OpenAI, including error handling for rate limits and API connection issues, and retries
    failed requests.

    Attributes:
        num_retries (int): The number of times to retry generating text upon encountering rate limits or
        connection errors.
    """
    num_retries = 5

    def __init__(self, model):
        """
        Initializes the GPT class with a specific model.

        Parameters:
            model (str): The identifier of the GPT model to use for generating text.
        """
        self._model = model
        self.logger = None

    def generate_text(self, model_prompt, **params):
        """
        Generates text based on the provided prompts and additional parameters for the GPT model.

        Parameters:
            model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
            **params: Arbitrary keyword arguments providing additional options to the model (e.g., temperature, max tokens).

        Returns:
            str or None: The generated text from the GPT model or None if the operation fails.

        Raises:
            APIError: If an API error occurs not related to rate limits or bad gateway responses.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        prompt = [
            {"role": "system", "content": model_prompt.get('System')},
            {"role": "user", "content": model_prompt.get('User')}
        ]

        # Will retry to get chat if a rate limit or bad gateway error is received from the chat
        reply = None
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = client.chat.completions.create(
                    model=self._model,
                    messages=prompt,
                    max_tokens=params["max_new_tokens"],
                    n=params["n"],
                    temperature=params["temperature"],
                    top_p=params["top_p"],
                    presence_penalty=params["penalty_alpha"],
                    stop=params["stop"],
                )

                reply = response.choices[0].message.content
                self.logger.log_response(reply)

                break

            except RateLimitError:
                self.logger.log("\n\nError: Reached API rate limit, retrying in 20 seconds...", 'warning')
                time.sleep(20)
            except APIConnectionError:
                self.logger.log("\n\nError: Connection issue, retrying in 2 seconds...", 'warning')
                time.sleep(2)
            except APIError as e:
                if getattr(e, 'status_code', None) == 502:
                    self.logger.log("\n\nError: Connection issue, retrying in 2 seconds...", 'warning')
                    time.sleep(backoff)
                else:
                    raise

        # reply will be none if we have failed above
        if reply is None:
            self.logger.log("\n\nError: Failed to get OpenAI Response", 'critical')

        return reply

