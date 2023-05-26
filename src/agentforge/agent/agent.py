from .func.agent_functions import AgentFunctions
from ..logs.logger_config import Logger


def calculate_next_task_order(this_task_order):
    return int(this_task_order) + 1


def order_tasks(task_list):
    filtered_results = [task for task in task_list if task['task_order'].isdigit()]

    ordered_results = [
        {'task_order': int(task['task_order']), 'task_desc': task['task_desc']}
        for task in filtered_results]

    return ordered_results


class Agent:
    def __init__(self, agent_name=None, log_level="info"):
        if agent_name is None:
            agent_name = self.__class__.__name__
        self.agent_funcs = AgentFunctions(agent_name)
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils
        self.logger = Logger(name=agent_name)
        self.logger.set_level(log_level)

    def parse_output(self, result, bot_id, data):
        return {"result": result}

    def run(self, bot_id=None, **kwargs):
        # This function will be the main entry point for your agent.
        self.logger.log(f"Running Agent...", 'info')

        # Load data
        data = {}
        if "database" in self.agent_data:
            db_data = self.load_data_from_memory()
            data.update(db_data)
        data.update(self.agent_data)
        data.update(kwargs)

        task_order = data.get('this_task_order')
        if task_order is not None:
            data['next_task_order'] = calculate_next_task_order(task_order)

        # Generate prompt
        prompt = self.generate_prompt(**data)

        # Execute the main task of the agent
        with self.agent_funcs.thinking():
            result = self.execute_task(prompt)

        parsed_data = self.parse_output(result, bot_id, data)

        # Stop Console Feedback
        self.agent_funcs.stop_thinking()

        output = None

        # Save and print the results
        if "result" in parsed_data:
            self.save_results(parsed_data)
            self.agent_funcs.print_result(parsed_data)
            output = parsed_data

        if "tasks" in parsed_data:
            ordered_tasks = order_tasks(parsed_data["tasks"])
            output = ordered_tasks
            task_desc_list = [task['task_desc'] for task in ordered_tasks]
            self.save_tasks(ordered_tasks, task_desc_list)
            self.agent_funcs.print_task_list(ordered_tasks)

        self.logger.log(f"Agent Done!", 'info')
        return output

    def load_result_data(self):
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]
        self.logger.log(f"Result Data Loaded:\n{result}", 'debug')

        return result

    def load_data_from_memory(self):
        raise NotImplementedError

    def render_template(self, template, variables, data):
        return template.format(
            **{k: v for k, v in data.items() if k in variables}
        )

    def generate_prompt(self, **kwargs):
        # Load Prompts from Persona Data
        prompts = self.agent_data['prompts']
        system_prompt = prompts['SystemPrompt']
        context_prompt = prompts['ContextPrompt']
        feedback_prompt = prompts['InstructionPrompt']
        instruction_prompt = prompts.get('FeedbackPrompt', {})

        system_prompt_template = system_prompt["template"]
        context_prompt_template = context_prompt["template"]
        instruction_prompt_template = instruction_prompt["template"]
        feedback_prompt_template = feedback_prompt["template"]

        system_prompt_vars = prompts['SystemPrompt']["vars"]
        context_prompt_vars = prompts['ContextPrompt']["vars"]
        instruction_prompt_vars = prompts['InstructionPrompt']["vars"]
        feedback_prompt_vars = prompts.get('FeedbackPrompt', {})["vars"]

        # Format Prompts
        templates = [
            (system_prompt_template, system_prompt_vars),
            (context_prompt_template, context_prompt_vars),
            (instruction_prompt_template, instruction_prompt_vars),
            (feedback_prompt_template, feedback_prompt_vars),
        ]
        user_prompt = "".join([
            self.render_template(template, variables, data=kwargs)
            for template, variables in templates]
        )

        # Build Prompt
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        self.logger.log(f"Prompt:\n{prompt}", 'debug')
        return prompt

    def execute_task(self, prompt):
        return self.agent_data['generate_text'](
            prompt,
            self.agent_data['model'],
            self.agent_data['params'],
        ).strip()

    def save_results(self, result, collection_name="results"):
        self.storage.save_results({
            'result': result,
            'collection_name': collection_name,
        })

    def save_tasks(self, ordered_results, task_desc_list):
        collection_name = "tasks"
        self.storage.clear_collection(collection_name)

        self.storage.save_tasks({
            'tasks': ordered_results,
            'results': task_desc_list,
            'collection_name': collection_name
        })
