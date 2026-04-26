import requests
import json
from .base_api import BaseModel
from agentforge.apis.mixins.vision_mixin import VisionMixin

class LMStudio(BaseModel):
    """
    Concrete implementation for OpenAI GPT models.
    """

    def _do_api_call(self, prompt, **filtered_params):
        if isinstance(prompt, dict) and "messages" in prompt:
            prompt = prompt["messages"]
        url = filtered_params.pop('host_url', 'http://localhost:1234/v1/chat/completions')
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": self.model_name,
            "messages": prompt,
            **filtered_params
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # return error content
            self.logger.error(f"Request error: {response}")
            return None

        return response.json()

    def _process_response(self, raw_response):
        return raw_response["choices"][0]["message"]["content"]


class LMStudioVision(VisionMixin, LMStudio):
    supported_modalities = {"text", "image"}

    def _merge_parts(self, parts, **params):
        messages = list(parts["text"])

        if "image" in parts and parts["image"]:
            if messages and messages[-1]["role"] == "user":
                content = [{"type": "text", "text": messages[-1]["content"]}]
                content.extend(parts["image"])
                messages[-1]["content"] = content

        return {"messages": messages, **params}