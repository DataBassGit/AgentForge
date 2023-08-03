import os
import time

import openai
from litellm import completion

from termcolor import cprint
from colorama import init
init(autoreset=True)

# litellm reads keys from env variables
# more info on how keys are read here: https://litellm.readthedocs.io/en/latest/supported/ 
# more info on using litellm is here: https://github.com/BerriAI/litellm/
_level = 'debug'


def parse_prompts(prompts):

    if _level == 'debug':
        prompt = ''.join(prompts)
        cprint(f'\nPrompt:\n"{prompt}"', 'magenta', attrs=['concealed'])

    prompt = [
        {"role": "system", "content": prompts[0]},
        {"role": "user", "content": "".join(prompts[1:])}
    ]

    return prompt


class liteLLM:
    num_retries = 5

    def __init__(self, model):
        self._model = model

    def generate_text(self, prompts, **params):
        reply = None
        prompt = parse_prompts(prompts)
        # will retry to get chat if a rate limit or bad gateway error is received
        # from the chat, up to limit of num_retries
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                # using litellm completion 
                # litellm allows usage of Anthropic/Google/Cohere/Replicate models using openai inputs/outputs
                # see https://litellm.readthedocs.io/en/latest/supported/
                response = completion(
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
                    raise
        # reply will be none if we have failed above
        if reply is None:
            raise RuntimeError("\n\nError: Failed to get liteLLM Response")

        return reply
