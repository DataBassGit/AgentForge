import sys
import threading
import time
import uuid
from typing import Dict, Any

from ..llm import LLM
from ..logs.logger_config import Logger
from .. import config

from ..utils.storage_interface import StorageInterface
from ..utils.function_utils import Functions

from termcolor import cprint
from colorama import init
init(autoreset=True)


def handle_prompt_type(prompts, prompt_type):
    """Handle each type of prompt and return template and vars."""
    prompt_data = prompts.get(prompt_type, {})
    if prompt_data:
        return [(prompt_data['template'], prompt_data['vars'])]
    return []


def set_feedback(data):
    feedback = data.get('feedback')
    if feedback is None:
        data['prompts'].pop('FeedbackPrompt', None)


def set_task_order(data):
    task_order = data.get('this_task_order')
    if task_order is not None:
        data['next_task_order'] = _calculate_next_task_order(task_order)


def show_task(data):
    if 'task' in data:
        cprint(f'\nTask: {data["task"]}', 'green', attrs=['dark'])


def _calculate_next_task_order(this_task_order):
    return int(this_task_order) + 1


def _render_template(template, variables, data):
    temp = template.format(
        **{k: v for k, v in data.items() if k in variables}
    )

    return temp


def fetch_context(kwargs):
        return {'context': kwargs.get('context', {}).get('result', "No Context Provided.")}


def fetch_task_result(kwargs):
    return {'result': kwargs['task_result']['result']}


def load_agent_data(agent_name):
    # Load persona data
    persona_data = config.persona()

    agent = persona_data[agent_name]
    defaults = persona_data['Defaults']

    api = agent.get('API', defaults['API'])
    params = agent.get('Params', defaults['Params'])

    # Initialize agent data
    agent_data: Dict[str, Any] = dict(
        name=agent_name,
        llm=config.get_llm(api, agent_name),
        objective=persona_data['Objective'],
        prompts=agent['Prompts'],
        params=params,
        storage=StorageInterface().storage_utils,
    )

    # ETHOS
    if "HeuristicImperatives" in persona_data:
        imperatives = persona_data["HeuristicImperatives"]
        agent_data.update(heuristic_imperatives=imperatives)

    return agent_data


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


class Agent:
    def __init__(self, agent_name=None, log_level="info"):
        if agent_name is None:
            agent_name = self.__class__.__name__

        self._spinner = Spinner()
        self.agent_data = load_agent_data(agent_name)
        self.storage = self.agent_data['storage']
        self.logger = Logger(name=agent_name)
        self.logger.set_level(log_level)

    def parse_output(self, result, bot_id, data):
        return {"result": result}

    def get_data(self, key, loader, kwargs, data, invert_logic=False):
        if ((key not in kwargs) and not invert_logic) or ((key in kwargs) and invert_logic):
            db_data = loader()
            if db_data is not None:
                data.update(db_data)
        return data

    def save_parsed_data(self, parsed_data):
        save_operations = {
            "result": (self.save_results, lambda data: data),
            "Tasks": (
            lambda tasks: self.save_tasks(tasks, [task['Description'] for task in tasks]), lambda data: data["Tasks"]),
            "status": (lambda status: self.save_status(status, parsed_data["task"]["task_id"],
                                                       parsed_data["task"]["description"],
                                                       parsed_data["task"]["order"]), lambda data: data)
        }

        output = None
        for key, (save_function, data_selector) in save_operations.items():
            if key in parsed_data:
                save_function(parsed_data[key])
                output = data_selector(parsed_data)

        return output

    def run(self, bot_id=None, **kwargs):
        agent_name = self.__class__.__name__
        # self.logger.log(f"Running Agent...", 'info')
        cprint(f"\n{agent_name} - Running Agent...", 'red', attrs=['bold'])

        context_data = kwargs.get('context') or {}
        context_result = context_data.get('result', "No Context Provided.")
        task_result_data = kwargs.get('task_result') or {}
        task_result = task_result_data.get('result', None)

        # Load data
        data = {}
        data = self.get_data("task", self.load_current_task, kwargs, data)
        data = self.get_data("task_list", self.load_data_from_memory, kwargs, data)
        data = self.get_data("context", lambda: {'context': context_result}, kwargs, data)
        data = self.get_data("task_result", lambda: {'result': task_result}, kwargs, data, invert_logic=True)
        data.update(self.agent_data, **kwargs)

        set_feedback(data)
        set_task_order(data)
        show_task(data)

        # Generate prompt
        prompts = self.generate_prompt(**data)

        # Execute the main task of the agent
        with self._spinner:
            result = self.run_llm(prompts)

        parsed_data = self.parse_output(result, bot_id, data)
        output = self.save_parsed_data(parsed_data)

        # self.logger.log(f"Agent Done!", 'info')
        cprint(f"\n{agent_name} - Agent Done...\n", 'red', attrs=['bold'])

        return output

    def load_result_data(self):
        result_collection = self.storage.load_collection({
            'collection_name': "Results",
            'include': ["documents"],
        })
        result = result_collection[0] if result_collection else ["No results found"]
        self.logger.log(f"Result Data Loaded:\n{result}", 'debug')

        return result

    def load_data_from_memory(self):
        pass

    def load_current_task(self):
        task_list = self.storage.load_collection({'collection_name': "Tasks", 'include': ["documents"]})
        task = task_list['documents'][0]
        return {'task': task}

    def generate_prompt(self, **kwargs):
        # Load Prompts from Persona Data
        prompts = self.agent_data['prompts']
        templates = []

        # Handle system prompt
        system_prompt = prompts['SystemPrompt']
        templates.append((system_prompt["template"], system_prompt["vars"]))

        # Handle other types of prompts
        for prompt_type in ['ContextPrompt', 'FeedbackPrompt', 'InstructionPrompt']:
            templates.extend(handle_prompt_type(prompts, prompt_type))

        prompts = [
            _render_template(template, variables, data=kwargs)
            for template, variables in templates
        ]

        self.logger.log(f"Prompt:\n{prompts}", 'debug')

        return prompts

    def run_llm(self, prompt):
        model: LLM = self.agent_data['llm']
        params = self.agent_data.get("params", {})
        return model.generate_text(prompt, **params,).strip()

    def save_results(self, result, collection_name="Results"):
        self.storage.save_memory({
            'data': [result],
            'collection_name': collection_name,
        })

    def save_tasks(self, ordered_results, task_desc_list):
        collection_name = "Tasks"
        self.storage.clear_collection(collection_name)

        metadatas = [{
            "Status": "not completed",
            "Description": task["Description"],
            "List_ID": str(uuid.uuid4()),
            "Order": task["Order"]
        } for task in ordered_results]

        task_orders = [task["Order"] for task in ordered_results]

        params = {
            "collection_name": collection_name,
            "ids": [str(order) for order in task_orders],
            "data": task_desc_list,
            "metadata": metadatas,
        }

        self.storage.save_memory(params)

    def save_status(self, status, task_id, text, task_order):
        self.logger.log(
            f"\nSave Task: {text}"
            f"\nSave ID: {task_id}"
            f"\nSave Order: {task_order}"
            f"\nSave Status: {status}",
            'debug'
        )
        params = {
            'collection_name': "Tasks",
            'ids': [task_id],
            'data': [text],
            'metadata': [{
                "Status": status,
                "Description": text,
                "Order": task_order,
            }]
        }
        self.storage.update_memory(params)
