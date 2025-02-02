import os
from .base_api import BaseModel
from groq import Groq
# from agentforge.utils.Logger import Logger

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

class GroqAPI(BaseModel):

    def _do_api_call(self, prompt, **filtered_params):
        response = client.chat.completions.create(
            model=self.model_name,
            messages=prompt,
            **filtered_params
        )
        return response

    def _process_response(self, raw_response):
        return raw_response.choices[0].message.content
