from .BaseAPI import BaseModel
from openai import OpenAI

# Assuming you have set OPENAI_API_KEY in your environment variables
client = OpenAI()

class GPT(BaseModel):
    """
    Concrete implementation for OpenAI GPT models.
    """

    def _do_api_call(self, prompt, **filtered_params):
        response = client.chat.completions.create(
            model=self.model_name,
            messages=prompt,
            **filtered_params
        )
        return response

    def _process_response(self, raw_response):
        return raw_response.choices[0].message.content

class Omni(GPT):
    """
    Concrete implementation for OpenAI GPT models.
    """

    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)
        self.allowed_params = {"stop"}

    def _prepare_prompt(self, model_prompt):
        # Format user messages in the appropriate style
        content = f"{model_prompt.get('System', '')}\n\n{model_prompt.get('User', '')}"
        return [{"role": "user", "content": content}]

