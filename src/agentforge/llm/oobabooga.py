import requests


class Oobabooga:
    def __init__(self, model):
        self._model = model

    @staticmethod
    def generate_text(prompt, **params):

        # Server address
        # url = f"http://{params['host_url']}/api/v1/generate"
        url = f"http://{params['host_url']}/v1/chat/completions"

        headers = {
            "Content-Type": "application/json"
        }

        request = {
            'prompt': str(prompt),
            'max_new_tokens': params['max_new_tokens'],
            'do_sample': params['do_sample'],
            'temperature': params['temperature'],
            'top_p': params['top_p'],
            'typical_p': params['typical_p'],
            'repetition_penalty': params['repetition_penalty'],
            'top_k': params['top_k'],
            'min_length': params['min_length'],
            'no_repeat_ngram_size': params['no_repeat_ngram_size'],
            'num_beams': params['num_beams'],
            'penalty_alpha': params['penalty_alpha'],
            'length_penalty': params['length_penalty'],
            'early_stopping': params['early_stopping'],
            'seed': params['seed'],
            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'skip_special_tokens': True,
            'stopping_strings': []
        }

        # print(f"prompt: {prompt}")
        reply = None

        response = requests.post(url, json=request)

        # if response.status_code == 200:
        #     reply = response.json()['results'][0]['text']
        #     # print(str(prompt) + reply)

        if response.status_code == 200:
            reply = response.json()['results'][0]['text']
            print(str(prompt) + reply)

        return reply
