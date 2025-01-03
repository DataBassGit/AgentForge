import os
import time
from .BaseAPI import BaseModel
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from agentforge.utils.Logger import Logger

# Get API key from Env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


class Gemini(BaseModel):
    """
    A class for interacting with Google's Generative AI models to generate text based on provided prompts.

    Handles API calls to Google's Generative AI, including error handling for rate limits and retries failed requests.
    """

    @staticmethod
    def _prepare_prompt(model_prompt):
        return '\n\n'.join([model_prompt.get('System'), model_prompt.get('User')])

    def _do_api_call(self, prompt, **filtered_params):
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            generation_config=genai.types.GenerationConfig(**filtered_params)
        )

        return response

    def _process_response(self, raw_response):
        return raw_response.text

    def generate_text(self, model_prompt, **params):
        """
        Generates text based on the provided prompts and additional parameters for the model.

        Parameters:
            model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
            **params: Arbitrary keyword arguments providing additional options to the model.

        Returns:
            str or None: The generated text from the model or None if the operation fails after retry attempts.

        This method attempts to generate content with the provided prompts and configuration, retrying up to a
        specified number of times with exponential backoff in case of errors. It logs the process and errors.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        prompt = '\n\n'.join([model_prompt.get('System'), model_prompt.get('User')])

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
                print(response)

                break

            except Exception as e:
                self.logger.log(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}", 'warning')
                time.sleep(backoff)

        # reply will be none if we have failed above
        if reply is None:
            self.logger.log("\n\nError: Failed to get Gemini Response", 'critical')

        return reply
