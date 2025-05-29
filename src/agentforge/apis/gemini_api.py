import os
import time
from .base_api import BaseModel
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from agentforge.utils.logger import Logger
from agentforge.apis.mixins.vision_mixin import VisionMixin

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
        # Return the standard messages format expected by base class
        return [
            {"role": "system", "content": model_prompt.get('system')},
            {"role": "user", "content": model_prompt.get('user')}
        ]

    def _do_api_call(self, prompt, **filtered_params):
        # Extract the actual prompt text from the messages format provided by base class
        if isinstance(prompt, dict) and "messages" in prompt:
            # Convert messages format to single prompt string
            messages = prompt["messages"]
            prompt_text = '\n\n'.join([msg["content"] for msg in messages if msg["content"]])
        else:
            prompt_text = prompt
            
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(
            prompt_text,
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


class GeminiVision(VisionMixin, Gemini):
    """
    Adds image support to Gemini via VisionMixin.
    Only _merge_parts needs tweaking to match Gemini's request schema.
    """
    def _merge_parts(self, parts, **params):
        # For Gemini, we need a list of content parts
        if isinstance(parts["text"], str):
            content = [parts["text"]]
        else:
            content = parts["text"]
            
        if "image" in parts:
            content.extend(parts["image"])
        return {"contents": content, **params}

