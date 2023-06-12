import os
import time

import openai

openai.api_key = os.environ.get('OPENAI_API_KEY')


class GPT:
    num_retries = 5

    def __init__(self, model):
        self._model = model

    def generate_text(self, prompt, **params):
        reply = None

        # will retry to get chat if a rate limit or bad gateway error is received
        # from the chat, up to limit of num_retries
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:

                response = openai.ChatCompletion.create(
                    model=self._model,
                    messages=prompt,
                    max_tokens=params["max_new_tokens"],
                    n=params["n"],
                    temperature=params["temperature"],
                    top_p=params["top_p"],
                    presence_penalty=params["penalty_alpha"],
                    stop=params["stop"],
                )
                reply = response.choices[0].message.content
                break

            except openai.error.RateLimitError:
                print("\n\nError: Reached API rate limit, retrying in 20 seconds...")
                time.sleep(20)
            except openai.error.APIError as e:
                if e.http_status == 502:
                    print(f"\n\nError: Bad gateway, retrying in {backoff} seconds...")
                    time.sleep(backoff)
                else:
                    raise from e

        # reply will be none if we have failed above
        if reply is None:
            raise RuntimeError("\n\nError: Failed to get OpenAI Response")

        return reply
