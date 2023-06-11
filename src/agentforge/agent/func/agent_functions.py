import sys
import threading
import time
from typing import Dict, Any

from ... import config
from ...utils.storage_interface import StorageInterface


def _set_model_api(language_model_api):
    if language_model_api == 'oobabooga_api':
        from ...llm.oobabooga_api import generate_text
    elif language_model_api == 'openai_api':
        from ...llm.openai_api import generate_text
    elif language_model_api == 'claude_api':
        from ...llm.claude_api import generate_text
    else:
        raise ValueError(
            f"Unsupported Language Model API library: {language_model_api}")

    return generate_text


class AgentFunctions:
    agent_data: Dict[str, Any]

    def __init__(self, agent_name):
        # Load persona data
        self.persona_data = config.persona()

        # Load API and Model
        language_model_api = self.persona_data[agent_name]['API']
        generate_text = _set_model_api(language_model_api)
        model = self.persona_data[agent_name]['Model']

        # Initialize agent data
        self.agent_data = dict(
            name=agent_name,
            generate_text=generate_text,
            storage=StorageInterface(),
            objective=self.persona_data['Objective'],
            model=config.model_library(model),
            prompts=self.persona_data[agent_name]['Prompts'],
            params=self.persona_data[agent_name]['Params'],
        )

        if "HeuristicImperatives" in self.persona_data:
            imperatives = self.persona_data["HeuristicImperatives"]
            self.agent_data.update(heuristic_imperatives=imperatives)


class Spinner:
    spinner_thread = None
    spinner_running = False

    def _spin(self):
        while self.spinner_running:
            for char in '|/-\\':
                sys.stdout.write(char)
                sys.stdout.flush()
                sys.stdout.write('\b')
                time.sleep(0.1)

    def __enter__(self):
        self.spinner_running = True
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.spinner_running = False
        if self.spinner_thread is not None:
            self.spinner_thread.join()  # wait for the spinner thread to finish
        sys.stdout.write(' ')  # overwrite the last spinner character
        sys.stdout.write('\b')  # move the cursor back one space
        sys.stdout.flush()
