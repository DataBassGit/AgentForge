from typing import Protocol
from termcolor import cprint
from colorama import init
init(autoreset=True)


class LLM(Protocol):
    def generate_text(self, prompt, **params):
        pass

    @staticmethod
    def print_prompt(prompt):
        cprint(f'\nPrompt:\n"{prompt}"', 'magenta', attrs=['concealed'])

    @staticmethod
    def print_response(response):
        cprint(f'\nModel Response:\n"{response}"', 'white', attrs=['concealed'])
