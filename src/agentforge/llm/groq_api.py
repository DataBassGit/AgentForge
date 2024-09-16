import os
from groq import Groq
from agentforge.utils.functions.Logger import Logger


class GroqAPI:

    def __init__(self, model):
        """
        Initializes the CustomAPI class.
        """
        self._model = model
        self.prompt_log = None
        self.prompt = None
        self.logger = None
        self.logger2 = None

    def generate_text(self, model_prompt, **params):
        """
        Sends a request to a custom AI model endpoint to generate a completion based on the provided prompt.

        This function constructs a request with specified parameters and sends it to a custom AI endpoint, which is
        expected to generate text based on the input prompt. The endpoint URL is read from an environment variable.

        Parameters:
            model_prompt (list): The prompt text to send to the model for generating a completion.
            **params: Arbitrary keyword arguments for future extensibility, not used currently.

        Returns:
            str or None: The JSON response from the AI model if the request is successful, None otherwise.

        Logs the prompt and the response using a Logger instance. If the `CUSTOM_AI_ENDPOINT` environment variable
        is not set or if the request fails, appropriate error messages are logged.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        prompt = self.parse_prompts(model_prompt)
        self.logger.log_prompt(self.prompt_log)
        api_key = os.getenv("GROQ_API_KEY")
        # url = "https://api.groq.com/openai/v1/models"
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": model_prompt[0]
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self._model,
            max_tokens=params['max_new_tokens'],
            seed=params['seed'],
            stop=params['stop'],
            temperature=params['temperature'],
            top_p=params['top_p'],
        )

        response_text = response.choices[0].message.content
        self.logger.log_response(response_text)

        if response.choices and response.choices[0].message:
            return response_text
        else:
            self.logger.log(f"Request error: {response}", 'error')
            return response

    def parse_prompts(self, prompts):
        """
        Formats a list of prompts into a single string formatted specifically for Groq's AI models.

        Parameters:
            prompts (list): A list of strings, each representing a segment of the overall prompt.

        Returns:
            str: A formatted prompt string combining human and AI prompt indicators with the original prompt content.
        """
        self.prompt = ''.join(prompts[1:])
        self.prompt_log = ''.join(prompts[0:])

        return self.prompt