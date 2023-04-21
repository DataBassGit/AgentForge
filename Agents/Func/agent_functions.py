import sys
import time
import threading
from typing import Dict, Any
from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface
from Personas.load_persona_data import load_persona_data


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

        # Initialize spinner
        self.spinner_running = True
        self.spinner_thread = threading.Thread(target=self._spinner_loop)

    def initialize_agent(self, agent_name):
        import configparser
        config = configparser.ConfigParser()
        config.read('Config/config.ini')

        # Load Storage Interface
        self.agent_data['storage'] = StorageInterface()

        # Load persona data
        self.persona_data = load_persona_data()
        self.agent_data['objective'] = self.persona_data['Objective']
        self.agent_data['params'] = self.persona_data[agent_name]['Params']
        self.agent_data['prompts'] = self.persona_data[agent_name]['Prompts']

        # Load API and Model
        language_model_api = self.persona_data[agent_name]['API']
        self.set_model_api(language_model_api)

        model = self.persona_data[agent_name]['Model']
        self.agent_data['model'] = config.get('ModelLibrary', model)

    def set_model_api(self, language_model_api):
        if language_model_api == 'oobabooga_api':
            from APIs.oobabooga_api import generate_text
        elif language_model_api == 'openai_api':
            from APIs.openai_api import generate_text
        else:
            raise ValueError(f"Unsupported Language Model API library: {language_model_api}")

        self.agent_data['generate_text'] = generate_text

    def run_llm(self, prompt):
        result = self.agent_data['generate_text'](prompt, self.agent_data['model'], self.agent_data['params']).strip()
        return result

    def print_task_list(self, ordered_results):
        self.functions.print_task_list(ordered_results)

    def print_result(self, result):
        self.functions.print_result(result)

    def _spinner_loop(self):
        msg = f"{self.agent_data['name']}: Thinking "
        while self.spinner_running:
            for char in "|/-\\":
                sys.stdout.write(msg + char)
                sys.stdout.flush()
                sys.stdout.write("\b" * (len(msg) + 1))
                time.sleep(0.1)

    def start_thinking(self):
        self.spinner_running = True
        self.spinner_thread = threading.Thread(target=self._spinner_loop)
        self.spinner_thread.start()

    def stop_thinking(self):
        self.spinner_running = False
        self.spinner_thread.join()

        # Clear spinner characters
        msg = f"{self.agent_data['name']}: Thinking "
        sys.stdout.write("\b" * len(msg + "\\"))

        # Write "Done." message and flush stdout
        sys.stdout.write(msg + "- Done.\n")
        sys.stdout.flush()