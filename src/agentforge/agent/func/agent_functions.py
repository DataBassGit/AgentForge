import sys
import threading
import time
from contextlib import contextmanager
from typing import Dict, Any

from ...config import loader
from ...utils.storage_interface import StorageInterface


class AgentFunctions:
    agent_data: Dict[str, Any]

    persona_data = None
    spinner_thread = None
    spinner_running = False

    def __init__(self, agent_name):

        # Initialize agent data
        self.agent_data = {
            'name': agent_name,
            'generate_text': None,
            'storage': None,
            'objective': None,
            'model': None,
            'prompts': None,
            'params': None
        }

        # Initialize agent
        self.initialize_agent(agent_name)

    def initialize_agent(self, agent_name):
        config = loader.Config()

        # Load persona data
        self.persona_data = config.persona()
        if "HeuristicImperatives" in self.persona_data:
            self.agent_data.update(
                heuristic_imperatives=self.persona_data["HeuristicImperatives"],
            )
        self.agent_data.update(
            storage=StorageInterface(),
            objective=self.persona_data['Objective'],
            params=self.persona_data[agent_name]['Params'],
            prompts=self.persona_data[agent_name]['Prompts'],
        )
        db = self.persona_data[agent_name].get('Database')
        if db:
            self.agent_data.update(database=db)

        # Load API and Model
        language_model_api = self.persona_data[agent_name]['API']
        self.set_model_api(language_model_api)

        model = self.persona_data[agent_name]['Model']
        self.agent_data['model'] = config.model_library(model)

    def set_model_api(self, language_model_api):
        if language_model_api == 'oobabooga_api':
            from ...llm.oobabooga_api import generate_text
        elif language_model_api == 'openai_api':
            from ...llm.openai_api import generate_text
        elif language_model_api == 'claudia_api':
            from ...llm.claudia_api import generate_text
        else:
            raise ValueError(
                f"Unsupported Language Model API library: {language_model_api}")

        self.agent_data['generate_text'] = generate_text

    def run_llm(self, prompt):
        result = self.agent_data['generate_text'](
            prompt,
            self.agent_data['model'],
            self.agent_data['params'],
        ).strip()
        return result

    def print_task_list(self, task_list):
        # Print the task list
        print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
        for t in task_list:
            print(str(t["task_order"]) + ": " + t["task_desc"])

    def _spinner(self):
        while self.spinner_running:
            for char in '|/-\\':
                sys.stdout.write(char)
                sys.stdout.flush()
                sys.stdout.write('\b')
                time.sleep(0.1)

    def start_thinking(self):
        self.spinner_running = True
        self.spinner_thread = threading.Thread(target=self._spinner)
        self.spinner_thread.start()

    def stop_thinking(self):
        self.spinner_running = False
        if self.spinner_thread is not None:
            self.spinner_thread.join()  # wait for the spinner thread to finish
        sys.stdout.write(' ')  # overwrite the last spinner character
        sys.stdout.write('\b')  # move the cursor back one space
        sys.stdout.flush()

    @contextmanager
    def thinking(self):
        try:
            self.start_thinking()
            yield
        finally:
            self.stop_thinking()
