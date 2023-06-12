import os
import time

import anthropic

API_KEY = os.environ.get('ANTHROPIC_API_KEY')
client = anthropic.Client(API_KEY)


def generate_text(prompt, model, params):
    reply = None
    num_retries = 5

    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        try:
            response = client.completion(
                prompt=prompt,
                stop_sequences=[anthropic.HUMAN_PROMPT],
                model=model,
                max_tokens_to_sample=params["max_new_tokens"],
                temperature=params["temperature"],
                top_p=params["top_p"]
            )
            reply = response
            break

        except anthropic.ApiException:
            print(f"\n\nError: Retrying in {backoff} seconds...")
            time.sleep(backoff)

    if reply is None:
        raise RuntimeError("\n\nError: Failed to get Anthropic Response")

    return reply
