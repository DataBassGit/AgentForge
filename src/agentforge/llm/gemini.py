import os
import time
import google.generativeai as genai
from agentforge.utils.functions.Logger import Logger

# Get API key from Env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


def parse_prompts(prompts):
    prompt = ''.join(prompts[0:])

    return prompt


class Gemini:
    num_retries = 5

    def __init__(self, model):
        self._model = genai.GenerativeModel(model)
        self.logger = Logger(name=__name__)

    def generate_text(self, prompts, **params):
        log_level = params.get('log_level', 'info')
        self.logger.set_level(log_level)

        prompt = parse_prompts(prompts)
        self.logger.log_prompt(prompt)

        # Will retry to get chat if a rate limit or bad gateway error is received from the chat
        reply = None
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
                self.logger.log_response(reply)

                break

            except Exception as e:
                self.logger.log(f"\n\nError: Retrying in {backoff} seconds...\nError Code: {e}", 'warning')
                time.sleep(backoff)

        # reply will be none if we have failed above
        if reply is None:
            self.logger.log("\n\nError: Failed to get Gemini Response", 'critical')

        return reply
