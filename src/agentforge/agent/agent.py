import uuid
from typing import Dict, Any
from ..llm import LLM
from ..logs.logger_config import Logger
from .. import config

from ..utils.storage_interface import StorageInterface

from termcolor import cprint
from colorama import init
init(autoreset=True)


def _calculate_next_task_order(this_task_order):
    return int(this_task_order) + 1


def _get_data(key, loader, kwargs, data, invert_logic=False):
    if ((key not in kwargs) and not invert_logic) or ((key in kwargs) and invert_logic):
        db_data = loader()
        if db_data is not None:
            data.update(db_data)
    return data


def _handle_prompt_type(prompts, prompt_type):
    """Handle each type of prompt and return template and vars."""
    prompt_data = prompts.get(prompt_type, {})
    if prompt_data:
        return [(prompt_data['template'], prompt_data['vars'])]
    return []


def _load_agent_data(agent_name):
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


def remove_prompt_if_none(prompts, kwargs):
    prompts_copy = prompts.copy()
    for prompt_type, prompt_data in prompts_copy.items():
        required_vars = prompt_data.get('vars', [])
        # If there are no required vars or all vars are empty, we keep the prompt
        if not required_vars or all(not var for var in required_vars):
            continue
        for var in required_vars:
            if kwargs.get(var) is None:
                prompts.pop(prompt_type)
                break  # Exit this loop, the dictionary has been changed


def _render_template(template, variables, data):
    temp = template.format(
        **{k: v for k, v in data.items() if k in variables}
    )

    return temp


def _show_task(data):
    if 'task' in data:
        cprint(f'\nTask: {data["task"]}', 'green', attrs=['dark'])


def _set_task_order(data):
    task_order = data.get('this_task_order')
    if task_order is not None:
        data['next_task_order'] = _calculate_next_task_order(task_order)


def _order_task_list(task_list):
    task_list.sort(key=lambda x: x["Order"])


class Agent:

    _agent_name = None

    def __init__(self, agent_name=None, log_level="info"):
        if agent_name is None:
            self._agent_name = self.__class__.__name__

        self.agent_data = _load_agent_data(self._agent_name)
        self.storage = self.agent_data['storage']
        self.logger = Logger(name=self._agent_name)
        self.logger.set_level(log_level)

    def run(self, bot_id=None, **kwargs):
        agent_name = self.__class__.__name__

        cprint(f"\n{agent_name} - Running Agent...", 'red', attrs=['bold'])

        data = self.load_and_process_data(**kwargs)
        prompts = self.generate_prompt(**data)
        result = self.run_llm(prompts)
        parsed_data = self.parse_result(result=result, data=data)

        self.save_parsed_data(parsed_data)

        output = self.build_output(parsed_data)

        cprint(f"\n{agent_name} - Agent Done...\n", 'red', attrs=['bold'])

        return output

    def generate_prompt(self, **kwargs):
        # Load Prompts from Persona Data
        prompts = kwargs['prompts']
        templates = []

        # Handle system prompt
        system_prompt = prompts['System']
        templates.append((system_prompt["template"], system_prompt["vars"]))

        # Remove prompts if there's no corresponding data in kwargs
        remove_prompt_if_none(prompts, kwargs)

        # Handle other types of prompts
        other_prompt_types = [prompt_type for prompt_type in prompts.keys() if prompt_type != 'System']
        for prompt_type in other_prompt_types:
            templates.extend(_handle_prompt_type(prompts, prompt_type))

        # Render Prompts
        prompts = [
            _render_template(template, variables, data=kwargs)
            for template, variables in templates
        ]

        self.logger.log(f"Prompt:\n{prompts}", 'debug')

        return prompts

    def get_task_list(self):
        return self.storage.load_collection({'collection_name': "Tasks",
                                             'include': ["documents", "metadatas"]})

    def load_and_process_data(self, **kwargs):
        # Load agent data
        self.agent_data = _load_agent_data(self._agent_name)

        # The data dict will contain all the data that the agent requires
        data = {'params': self.agent_data.get('params').copy(), 'prompts': self.agent_data['prompts'].copy()}

        # Add any other data needed by the agent from kwargs
        for key in kwargs:
            data[key] = kwargs[key]

        # Load additional data from storage that was not passed in kwargs
        self.load_additional_data(data)

        return data

    def load_additional_data(self, data):
        # By default, it does nothing, each agent should override this function to load any additional data
        # # Add 'objective' to the data
        data['objective'] = self.agent_data.get('objective')
        data['task'] = self.load_current_task()['task']

        _set_task_order(data)
        _show_task(data)

    def load_current_task(self):
        task_list = self.get_task_list()
        task = task_list['documents'][0]
        return {'task': task}

    def parse_result(self, result, **kwargs):
        return {"Result": result}

    def run_llm(self, prompt):
        model: LLM = self.agent_data['llm']
        params = self.agent_data.get("params", {})
        return model.generate_text(prompt, **params,).strip()

    def build_output(self, parsed_data):
        build_operations = self.get_build_operations(parsed_data)
        output = parsed_data
        for key, data_selector in build_operations.items():
            if key in parsed_data:
                output = data_selector(parsed_data)
                break

        return output

    def save_parsed_data(self, parsed_data):
        save_operations = self.get_save_operations(parsed_data)
        for key, save_function in save_operations.items():
            if key in parsed_data:
                save_function(parsed_data[key])

    def save_results(self, result):
        params = {
            'data': [result],
            'collection_name': "Results",
        }

        self.storage.save_memory(params)

    def save_tasks(self, parsed_data):
        collection_name = "Tasks"
        self.storage.clear_collection(collection_name)

        ordered_results = parsed_data['tasks']
        task_desc_list = [task['Description'] for task in ordered_results]

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

    def get_build_operations(self, parsed_data):
        build_operations = {
            "Result": (lambda data: data),
        }

        return build_operations

    def get_save_operations(self, parsed_data):
        save_operations = {
            "Result": self.save_results
        }

        return save_operations

