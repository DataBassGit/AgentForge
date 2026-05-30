import os
from .base_api import BaseModel, ModelResponseError, NonRetriableModelError
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.generativeai.types.generation_types import GenerationConfig
from agentforge.apis.mixins.vision_mixin import VisionMixin


class Gemini(BaseModel):
    """
    A class for interacting with Google's Generative AI models to generate text based on provided prompts.

    Handles API calls to Google's Generative AI, including error handling for rate limits and retries failed requests.
    """

    @staticmethod
    def _prepare_prompt(model_prompt):
        # Return the standard messages format expected by base class
        return [
            {"role": "system", "content": model_prompt.get("system")},
            {"role": "user", "content": model_prompt.get("user")},
        ]

    def _do_api_call(self, prompt, **filtered_params):
        self._ensure_configured()
        model = GenerativeModel(self.model_name)

        # Handle different prompt formats
        if isinstance(prompt, dict):
            if "contents" in prompt:
                # GeminiVision format - pass contents directly
                content = prompt["contents"]
            elif "messages" in prompt:
                # Standard messages format - convert to text
                messages = prompt["messages"]
                content = "\n\n".join([msg["content"] for msg in messages if msg["content"]])
            else:
                content = prompt
        else:
            content = prompt

        response = model.generate_content(
            content,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            generation_config=GenerationConfig(**filtered_params),
        )

        return response

    @staticmethod
    def _ensure_configured():
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise NonRetriableModelError("GOOGLE_API_KEY is not set. Export GOOGLE_API_KEY before using Gemini models.")
        configure(api_key=api_key)

    def _process_response(self, raw_response):
        try:
            text = raw_response.text
        except Exception as exc:
            candidates = getattr(raw_response, "candidates", None)
            raise ModelResponseError(
                f"Gemini received a malformed response for model '{self.model_name}'. Candidates: {candidates!r}"
            ) from exc

        if not isinstance(text, str) or not text.strip():
            raise ModelResponseError(f"Gemini received an empty response for model '{self.model_name}'.")
        return text


class GeminiVision(VisionMixin, Gemini):
    """
    Adds image support to Gemini via VisionMixin.
    Only _merge_parts needs tweaking to match Gemini's request schema.
    """

    def _merge_parts(self, parts, **params):
        # For Gemini, we need to format content properly for the Google Generative AI library
        content = []

        # Add text content
        if "text" in parts:
            text_parts = parts["text"]
            if isinstance(text_parts, list):
                for msg in text_parts:
                    if isinstance(msg, dict) and "content" in msg:
                        content.append(msg["content"])
                    else:
                        content.append(str(msg))
            else:
                content.append(str(text_parts))

        # Add image content
        if "image" in parts:
            # Convert from VisionMixin format to Google format
            for img_part in parts["image"]:
                if isinstance(img_part, dict) and "image_url" in img_part:
                    # Extract base64 data from data URL
                    url = img_part["image_url"]["url"]
                    if url.startswith("data:image/"):
                        # Extract the base64 part after the comma
                        base64_data = url.split(",", 1)[1]
                        # Google Generative AI expects PIL Image or raw bytes
                        import base64
                        import io
                        from PIL import Image

                        image_bytes = base64.b64decode(base64_data)
                        image = Image.open(io.BytesIO(image_bytes))
                        content.append(image)

        return {"contents": content, **params}
