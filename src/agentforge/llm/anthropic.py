import os
import time
import anthropic
from ..llm import LLM

from termcolor import cprint
from colorama import init
init(autoreset=True)

API_KEY = os.getenv('ANTHROPIC_API_KEY')
client = anthropic.Anthropic(api_key=API_KEY)


def parse_prompts(prompts):
    prompt = ''.join(prompts[0:])
    prompt = f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}"

    return prompt


class Claude:
    num_retries = 5

    def __init__(self, model):
        self._model = model

    def generate_text(self, prompts, **params):
        response = None
        prompt = parse_prompts(prompts)

        if params.get('show_prompt', False):
            LLM.print_prompt(prompt)

        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = client.completions.create(
                    prompt=prompt,
                    # stop_sequences=[anthropic.HUMAN_PROMPT],
                    model=self._model,
                    max_tokens_to_sample=params["max_new_tokens"],
                    temperature=params["temperature"],
                    top_p=params["top_p"]
                )

                if params.get('show_model_response', False):
                    LLM.print_response(response)
                break

            except anthropic.ApiException as e:
                print(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}")
                time.sleep(backoff)

        if response is None:
            raise RuntimeError("\n\nError: Failed to get Anthropic Response")

        return response.completion
