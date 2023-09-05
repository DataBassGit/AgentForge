import requests


class Oobabooga:
    _server = "127.0.0.1"

    def generate_text(self, prompt, **params):
        print("prompt:" + prompt)

        data = [
            prompt,
            params['max_new_tokens'],
            params['do_sample'],
            params['temperature'],
            params['top_p'],
            params['typical_p'],
            params['repetition_penalty'],
            params['encoder_repetition_penalty'],
            params['top_k'],
            params['min_length'],
            params['no_repeat_ngram_size'],
            params['num_beams'],
            params['penalty_alpha'],
            params['length_penalty'],
            params['early_stopping'],
            params['seed']
        ]
        with requests.Session() as session:
            response = session.post(f"http://{self._server}:7860/run/textgen",
                                    json={"data": data}).json()
            print(response)
            reply = response["data"][0]

        return reply


class OobaboogaV2:
    # Server address
    _server = "127.0.0.1:5000"
    # For local streaming, the websockets are hosted without ssl - http://
    # HOST = 'localhost:5000'
    _uri = f'http://{_server}/api/v1/generate'

    def generate_text(self, prompt, **params):
        reply = None

        print(f"prompt: {prompt}")

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
        # with requests as session:
        with requests.Session() as session:
            response = session.post(self._uri, json=request)

            if response.status_code == 200:
                reply = response.json()['results'][0]['text']
                print(str(prompt) + reply)

        return reply
