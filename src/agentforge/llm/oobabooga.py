# import sseclient  # pip install sseclient-py
import requests
from agentforge.utils.functions.Logger import Logger


class Oobabooga:
    """
    A class for interacting with an external text generation service named Oobabooga. This class handles the
    construction and execution of requests to the Oobabooga API to generate text based on a given prompt.

    Attributes:
        _model (str): The model identifier used for generating text. This is kept for compatibility but may not
                      be directly used depending on the external service's API.
    """
    def __init__(self, model):
        """
        Initializes the Oobabooga class with a specific model identifier.

        Parameters:
            model (str): The identifier of the model to use for text generation.
        """
        self._model = model
        self.logger = None

    def generate_text(self, prompt, **params):
        """
        Generates text based on the provided prompt and additional parameters by making a request to the
        Oobabooga service's API.

        Parameters:
            prompt (str or list): The prompt or prompts to send to the text generation service. If a list,
                                  it will be joined into a single string.
            **params: Arbitrary keyword arguments providing additional options for the request. This includes
                      'agent_name' for logging purposes and 'host_url' for specifying the Oobabooga service's address.

        Returns:
            str: The generated text from the Oobabooga service.

        Raises:
            Exception: Logs a critical error message if an exception occurs during the API request.
        """
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        prompt = ''.join(prompt)
        self.logger.log_prompt(prompt)

        # Server address
        host = params.pop('host_url', None)
        url = f"{host}/v1/chat/completions"

        headers = {"Content-Type": "application/json"}

        message = [{"role": "user", "content": prompt}]

        # request = {
        #     'prompt': str(prompt),
        #     'max_new_tokens': params['max_new_tokens'],
        #     'do_sample': params['do_sample'],
        #     'temperature': params['temperature'],
        #     'top_p': params['top_p'],
        #     'typical_p': params['typical_p'],
        #     'repetition_penalty': params['repetition_penalty'],
        #     'top_k': params['top_k'],
        #     'min_length': params['min_length'],
        #     'no_repeat_ngram_size': params['no_repeat_ngram_size'],
        #     'num_beams': params['num_beams'],
        #     'penalty_alpha': params['penalty_alpha'],
        #     'length_penalty': params['length_penalty'],
        #     'early_stopping': params['early_stopping'],
        #     'seed': params['seed'],
        #     'add_bos_token': True,
        #     'truncation_length': 2048,
        #     'ban_eos_token': False,
        #     'skip_special_tokens': True,
        #     'stopping_strings': []
        # }

        # data = {
        #     "prompt": "This is a cake recipe:\n\n1.",
        #     "max_tokens": 200,
        #     "temperature": 1,
        #     "top_p": 0.9,
        #     "seed": 10,
        #     "stream": False,
        # }

        # data = {
        #     "mode": "instruct",
        #     "stream": True,
        #     "messages": message
        # }

        data = {
            "mode": "chat",
            "character": "Example",
            "messages": message
        }

        reply = ''
        try:
            response = requests.post(url, headers=headers, json=data, verify=False)

            reply = response.json()['choices'][0]['message']['content']
            self.logger.log_response(reply)

            # stream_response = requests.post(url, headers=headers, json=data, verify=False, stream=True)
            # client = sseclient.SSEClient(stream_response)
            #
            # assistant_message = ''
            # for event in client.events():
            #     payload = json.loads(event.data)
            #     chunk = payload['choices'][0]['message']['content']
            #     assistant_message += chunk
            #     print(chunk, end='')
            #
            # print()

        except Exception as e:
            self.logger.log(f"\n\nError: {e}", 'critical')

        # if response.status_code == 200:
        #     reply = response.json()['results'][0]['text']
        #     # print(str(prompt) + reply)
        #
        # if response.status_code == 200:
        #     reply = response.json()['results'][0]['text']
        #     print(str(prompt) + reply)
        # else:
        #     print(reply)

        return reply
