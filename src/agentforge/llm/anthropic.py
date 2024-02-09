import os
import time
import anthropic
from agentforge.utils.functions.Logger import Logger

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
        self.logger = Logger(name=__name__)

    def generate_text(self, prompts, **params):
        log_level = params.get('log_level', 'info')
        self.logger.set_level(log_level)
        prompt = parse_prompts(prompts)
        self.logger.log_prompt(prompt)

        # Will retry to get chat if a rate limit or bad gateway error is received from the chat
        response = None
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
                self.logger.log_response(response)
                break

            except anthropic as e:
                self.logger.log(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}", 'warning')
                time.sleep(backoff)

        if response is None:
            self.logger.log("\n\nError: Failed to get Anthropic Response", 'critical')

        return response.completion
