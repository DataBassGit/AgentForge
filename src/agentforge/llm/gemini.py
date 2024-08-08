import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from agentforge.utils.functions.Logger import Logger

# Get API key from Env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


def parse_prompts(prompts):
    """
    Concatenates a list of prompt segments into a single string prompt.

    Parameters:
        prompts (list): A list of strings to be concatenated into a single prompt.

    Returns:
        str: A single string containing the concatenated prompt.
    """
    prompt = ''.join(prompts[0:])

    return prompt


class Gemini:
    """
    A class for interacting with Google's Generative AI models to generate text based on provided prompts.

    Handles API calls to Google's Generative AI, including error handling for rate limits and retries failed requests.

    Attributes:
        num_retries (int): The number of times to retry generating text upon encountering errors.
    """
    num_retries = 4

    def __init__(self, model):
        """
        Initializes the Gemini class with a specific Generative AI model from Google.

        Parameters:
            model (str): The identifier of the Google Generative AI model to use for generating text.
        """
        self._model = genai.GenerativeModel(model)
        self.logger = None

    def generate_text(self, prompts, **params):
        """
        Generates text based on the provided prompts and additional parameters for the model.

        Parameters:
            prompts (list): A list of strings to be passed as prompts to the model.
            **params: Arbitrary keyword arguments providing additional options to the model.

        Returns:
            str or None: The generated text from the model or None if the operation fails after retry attempts.

        This method attempts to generate content with the provided prompts and configuration, retrying up to a
        specified number of times with exponential backoff in case of errors. It logs the process and errors.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))

        prompt = parse_prompts(prompts)
        self.logger.log_prompt(prompt)

        # Will retry to get chat if a rate limit or bad gateway error is received from the chat
        reply = None
        for attempt in range(self.num_retries):
            backoff = 8 ** (attempt + 2)
            try:
                response = self._model.generate_content(
                    prompt,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    },
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=params["max_new_tokens"],
                        temperature=params["temperature"],
                        top_p=params.get("top_p", 1),
                        top_k=params.get("top_k", 1),
                        candidate_count=max(params.get("candidate_count", 1),1)
                    )
                )

                reply = response.text
                self.logger.log_response(reply)

                break

            except Exception as e:
                self.logger.log(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}", 'warning')
                time.sleep(backoff)

        # reply will be none if we have failed above
        if reply is None:
            self.logger.log("\n\nError: Failed to get Gemini Response", 'critical')

        return reply
