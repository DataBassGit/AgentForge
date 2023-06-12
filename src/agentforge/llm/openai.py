import os
import time

import openai
from openai.error import APIError, RateLimitError

openai.api_key = os.getenv('OPENAI_API_KEY')


def generate_text(prompt, model, params):
    reply = None
    num_retries = 5  # currently hardcoded but should be made configurable

    # will retry to get chat if a rate limit or bad gateway error is received
    # from the chat, up to limit of num_retries
    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        try:

            response = openai.ChatCompletion.create(
                model=model,
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

        except RateLimitError:
            print("\n\nError: Reached API rate limit, retrying in 20 seconds...")
            time.sleep(20)
        except APIError as e:
            if e.http_status == 502:
                print(
                    "\n\nError: Bad gateway, retrying in {} seconds...".format(backoff))
                time.sleep(backoff)
            else:
                raise

    # reply will be none if we have failed above
    if reply is None:
        raise RuntimeError("\n\nError: Failed to get OpenAI Response")

    return reply
