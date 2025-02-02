import os
import time
from .base_api import BaseModel
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from agentforge.utils.logger import Logger

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
        return '\n\n'.join([model_prompt.get('system'), model_prompt.get('user')])

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

