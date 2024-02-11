# import sseclient  # pip install sseclient-py
import requests
from agentforge.utils.functions.Logger import Logger


class Oobabooga:
    def __init__(self, model):
        self._model = model
        self.logger = None

    def generate_text(self, prompt, **params):
        self.logger = Logger(name=params.pop('agent_name', None))
        prompt = ''.join(prompt)
        self.logger.log_prompt(prompt)

        # Server address
        host = params.pop('host_url', None)
        url = f"http://{host}/v1/chat/completions"
        # url = f"http://{host}/v1/completions"

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
