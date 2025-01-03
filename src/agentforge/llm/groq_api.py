import os
from .BaseAPI import BaseModel
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

    # def __init__(self, model):
    #     """
    #     Initializes the CustomAPI class.
    #     """
    #     self._model = model
    #     self.prompt_log = None
    #     self.prompt = None
    #     self.logger = None
    #     self.logger2 = None

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
    #
    #     response = client.chat.completions.create(
    #         messages=[
    #             {"role": "system", "content": model_prompt.get('System')},
    #             {"role": "user", "content": model_prompt.get('User')}
    #         ],
    #         model=self._model,
    #         max_tokens=params['max_new_tokens'],
    #         seed=params['seed'],
    #         stop=params['stop'],
    #         temperature=params['temperature'],
    #         top_p=params['top_p'],
    #     )
    #
    #     response_text = response.choices[0].message.content
    #     self.logger.log_response(response_text)
    #
    #     if response.choices and response.choices[0].message:
    #         return response_text
    #     else:
    #         self.logger.log(f"Request error: {response}", 'error')
    #         return response