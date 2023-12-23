import os
import time
import google.generativeai as genai

from termcolor import cprint
from colorama import init
init(autoreset=True)

# Get API key from Env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

_level = 'debug'


def parse_prompts(prompts):
    prompt = ''.join(prompts[0:])

    if _level == 'debug':
        cprint(f'\nPrompt:\n"{prompt}"', 'magenta', attrs=['concealed'])

    return prompt


class Gemini:
    num_retries = 5

    def __init__(self, model):
        self._model = genai.GenerativeModel(model)

    def generate_text(self, prompts, **params):
        reply = None
        prompt = parse_prompts(prompts)
        # will retry to get chat if a rate limit or bad gateway error is received
        # from the chat, up to limit of num_retries
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = self._model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=params["max_new_tokens"],
                        temperature=params["temperature"],
                        top_p=params.get("top_p", 1),
                        top_k=params.get("top_k", 1),
                        candidate_count=max(params.get("candidate_count", 1),1)
                    )
                )
                reply = response.text
                break

            except Exception as e:
                print(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}")
                time.sleep(backoff)

        # reply will be none if we have failed above
        if reply is None:
            raise RuntimeError("\n\nError: Failed to get OpenAI Response")

        return reply
