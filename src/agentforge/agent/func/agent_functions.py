import sys
import threading
import time
from contextlib import contextmanager
from typing import Dict, Any

from ...config import loader
from ...utils.function_utils import Functions
from ...utils.storage_interface import StorageInterface


class AgentFunctions:
    agent_data: Dict[str, Any]

    functions = None
    persona_data = None
    spinner_thread = None

    def __init__(self, agent_name):

        # Initialize functions
        self.functions = Functions()

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

    def print_task_list(self, ordered_results):
        self.functions.print_task_list(ordered_results)

    def print_result(self, result):
        self.functions.print_result(result, self.agent_data['name'])

    def start_thinking(self):
        print("Thinking...")

    def stop_thinking(self):
        print("Done.\n")

    @contextmanager
    def thinking(self):
        try:
            self.start_thinking()
            yield
        finally:
            self.stop_thinking()
