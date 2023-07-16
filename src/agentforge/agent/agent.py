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

from termcolor import colored, cprint
from colorama import init
init(autoreset=True)


def _calculate_next_task_order(this_task_order):
    return int(this_task_order) + 1


# def _print_task_list(task_list):
#     # Print the task list
#     print("\033[95m\033[1m" + "\n*****TASK MY TESTING LIST*****\n" + "\033[0m\033[0m")
#     for t in task_list:
#         print(str(t["Order"]) + ": " + t["Description"])


def _render_template(template, variables, data):
    temp = template.format(
        **{k: v for k, v in data.items() if k in variables}
    )



    return temp


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

    def run(self, bot_id=None, **kwargs):
        agent_name = self.__class__.__name__
        # This function will be the main entry point for your agent.
        # self.logger.log(f"Running Agent...", 'info')
        cprint(f"\n{agent_name} - Running Agent...", 'red', attrs=['bold'])

        # Load data
        data = {}

        if "task" not in kwargs:
            db_data = self.load_current_task()
            data.update(db_data)
        if "task_list" not in kwargs:
            db_data = self.load_data_from_memory()
            if db_data is not None:
                data.update(db_data)
        if "context" not in kwargs:
            db_data = {'context': "No Context Provided."}
            data.update(db_data)
        if "task_result" in kwargs:
            db_data = {'result': kwargs['task_result']['result']}
            data.update(db_data)

        data.update(self.agent_data)
        data.update(kwargs)

        task_order = data.get('this_task_order')
        if task_order is not None:
            data['next_task_order'] = _calculate_next_task_order(task_order)

        # Generate prompt
        prompts = self.generate_prompt(**data)

        # prompt_output = '\n'.join([prompt['content'] for prompt in prompts])
        # cprint(f"\n{prompt_output}", 'magenta', attrs=['blink'])
        cprint(f"\n{prompts}", 'magenta', attrs=['blink'])

        # Execute the main task of the agent
        with self._spinner:
            result = self.run_llm(prompts)

        parsed_data = self.parse_output(result, bot_id, data)

        output = None

        # self.logger.log(f"Agent Done!", 'info')
        cprint(f"\n{agent_name} - Agent Done...\n", 'red', attrs=['bold'])

        # Save and print the results
        if "result" in parsed_data:
            self.save_results(parsed_data["result"])
            output = parsed_data

        if "Tasks" in parsed_data:
            ordered_tasks = parsed_data["Tasks"]
            output = parsed_data["Tasks"]
            task_desc_list = [task['Description'] for task in ordered_tasks]
            self.save_tasks(ordered_tasks, task_desc_list)
            # _print_task_list(ordered_tasks)

        if "status" in parsed_data:
            task_id = parsed_data["task"]["task_id"]
            description = parsed_data["task"]["description"]
            order = parsed_data["task"]["order"]
            status = parsed_data["status"]
            reason = parsed_data["reason"]
            output = reason
            self.save_status(status, task_id, description, order)

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
        task_list = self.storage.load_collection({
            'collection_name': "Tasks",
            'include': ["documents"],
        })
        task = task_list['documents'][0]
        return {'task': task}

    def generate_prompt(self, **kwargs):
        # Load Prompts from Persona Data
        prompts = self.agent_data['prompts']
        system_prompt = prompts['SystemPrompt']
        instruction_prompt = prompts.get('InstructionPrompt', {})
        context_prompt = prompts.get('ContextPrompt', {})
        feedback_prompt = prompts.get('FeedbackPrompt', {})

        system_prompt_template = system_prompt["template"]

        system_prompt_vars = system_prompt["vars"]

        # Format Prompts
        templates = [
            (system_prompt_template, system_prompt_vars),
        ]

        if context_prompt:
            context_prompt_template = context_prompt["template"]
            context_prompt_vars = context_prompt["vars"]
            templates.append(
                (context_prompt_template, context_prompt_vars),
            )

        if feedback_prompt and "feedback" in kwargs:
            feedback_prompt_template = feedback_prompt["template"]
            feedback_prompt_vars = feedback_prompt["vars"]
            templates.append(
                (feedback_prompt_template, feedback_prompt_vars)
            )

        if instruction_prompt:
            instruction_prompt_template = instruction_prompt["template"]
            instruction_prompt_vars = instruction_prompt["vars"]
            templates.append(
                (instruction_prompt_template, instruction_prompt_vars),
            )

        rendered_templates = [
            _render_template(template, variables, data=kwargs)
            for template, variables in templates
        ]

        # Build Prompt OPEN AI
        prompt = [
            {"role": "system", "content": rendered_templates[0]},
            {"role": "user", "content": "".join(rendered_templates[1:])}
        ]

        # prompt_output = '\n'.join([prompt['content'] for prompt in prompts])
        prompt_output = ''.join(rendered_templates[0:])
        prompt = "\n\nHuman: " + prompt_output + "\n\nAssistant:"

        self.logger.log(f"Prompt:\n{prompt}", 'debug')
        return prompt

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
