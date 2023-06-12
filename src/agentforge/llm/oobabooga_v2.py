import requests

# Server address
server = "127.0.0.1:5000"
# For local streaming, the websockets are hosted without ssl - http://
# HOST = 'localhost:5000'
URI = f'http://{server}/api/v1/generate'


class OobaboogaV2:
    def generate_text(self, prompt, **params):
        reply = None

        print(f"prompt: {prompt}")

        request = {
            'prompt': prompt,
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
        with requests.Session() as session:
            response = session.post(URI, json=request)

            if response.status_code == 200:
                reply = response.json()['results'][0]['text']
                print(prompt + reply)

        return reply
