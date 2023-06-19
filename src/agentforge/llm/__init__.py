from typing import Protocol


class LLM(Protocol):
    def generate_text(self, prompt, **params):
        pass
