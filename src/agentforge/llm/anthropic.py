import os
import time

import anthropic

API_KEY = os.environ.get('ANTHROPIC_API_KEY')
client = anthropic.Client(API_KEY)


class Claude:
    num_retries = 5

    def __init__(self, model):
        self._model = model

    def generate_text(self, prompt, **params):
        reply = None

        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = client.completion(
                    prompt=f"{anthropic.HUMAN_PROMPT}{prompt}{anthropic.AI_PROMPT}",
                    stop_sequences=[anthropic.HUMAN_PROMPT],
                    model=self._model,
                    max_tokens_to_sample=params["max_new_tokens"],
                    temperature=params["temperature"],
                    top_p=params["top_p"]
                )
                reply = response
                break

            except anthropic.ApiException as e:
                print(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}")
                time.sleep(backoff)

        if reply is None:
            raise RuntimeError("\n\nError: Failed to get Anthropic Response")

        return reply['completion']
