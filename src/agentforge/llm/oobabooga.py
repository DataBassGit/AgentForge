import requests


class Oobabooga:
    _server = "127.0.0.1"

    def generate_text(self, prompt, params):
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
