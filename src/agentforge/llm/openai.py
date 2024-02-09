import time
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from agentforge.utils.functions.Logger import Logger

# Assuming you have set OPENAI_API_KEY in your environment variables
client = OpenAI()


def parse_prompts(prompts):
    prompt = [
        {"role": "system", "content": prompts[0]},
        {"role": "user", "content": "".join(prompts[1:])}
    ]

    return prompt


class GPT:
    num_retries = 5

    def __init__(self, model):
        self._model = model
        self.logger = Logger(name=__name__)

    def generate_text(self, prompts, **params):
        log_level = params.get('log_level', 'info')
        self.logger.set_level(log_level)
        self.logger.log_prompt(''.join(prompts))

        prompt = parse_prompts(prompts)

        # Will retry to get chat if a rate limit or bad gateway error is received from the chat
        reply = None
        for attempt in range(self.num_retries):
            backoff = 2 ** (attempt + 2)
            try:
                response = client.chat.completions.create(
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
                self.logger.log_response(reply)

                break

            except RateLimitError:
                self.logger.log("\n\nError: Reached API rate limit, retrying in 20 seconds...", 'warning')
                time.sleep(20)
            except APIConnectionError:
                self.logger.log("\n\nError: Connection issue, retrying in 2 seconds...", 'warning')
                time.sleep(2)
            except APIError as e:
                if getattr(e, 'status_code', None) == 502:
                    self.logger.log("\n\nError: Connection issue, retrying in 2 seconds...", 'warning')
                    time.sleep(backoff)
                else:
                    raise

        # reply will be none if we have failed above
        if reply is None:
            self.logger.log("\n\nError: Failed to get OpenAI Response", 'critical')

        return reply

