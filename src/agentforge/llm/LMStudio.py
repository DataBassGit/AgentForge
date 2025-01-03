import requests
import json
from .BaseAPI import BaseModel

class LMStudio(BaseModel):
    """
    Concrete implementation for OpenAI GPT models.
    """

    def _do_api_call(self, prompt, **filtered_params):
        headers = {'Content-Type': 'application/json'}
        data = {
            "model": self.model_name,
            "messages": prompt,
            **filtered_params
        }

        url = filtered_params.pop('host_url', 'http://localhost:1234/v1/chat/completions')
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            # return error content
            self.logger.log(f"Request error: {response}", 'error')
            return None

        return response.json()

    def _process_response(self, raw_response):
        return raw_response["choices"][0]["message"]["content"]

    # def generate_text(self, model_prompt, **params):
    #     """
    #     Sends a request to a custom AI model endpoint to generate a completion based on the provided prompt.
    #
    #     This function constructs a request with specified parameters and sends it to a custom AI endpoint, which is
    #     expected to generate text based on the input prompt. The endpoint URL is read from an environment variable.
    #
    #     Parameters:
    #         model_prompt (dict[str]): A dictionary containing the model prompts for generating a completion.
    #         **params: Arbitrary keyword arguments for future extensibility, not used currently.
    #
    #     Returns:
    #         str or None: The JSON response from the AI model if the request is successful, None otherwise.
    #
    #     Logs the prompt and the response using a Logger instance. If the `CUSTOM_AI_ENDPOINT` environment variable
    #     is not set or if the request fails, appropriate error messages are logged.
    #     """
    #     self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
    #     self.logger.log_prompt(model_prompt)
    #
    #
    #     message_content = response_dict["choices"][0]["message"]["content"]
    #
    #     # self.logger.log_response(response.json()['response'])
    #     self.logger.log_response(message_content)


