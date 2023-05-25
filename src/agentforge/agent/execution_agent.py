from Agents.Func.agent_functions import AgentFunctions
from Logs.logger_config import Logger

logger = Logger(name="Execution Agent")


class ExecutionAgent:
    agent_data = None
    agent_funcs = None
    storage = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('ExecutionAgent')
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils
        logger.set_level('info')

    def run_execution_agent(self, context, feedback):
        logger.log(f"Running Agent...", 'info')

        logger.log(f"Context:{context}", 'info')

        task = self.load_data_from_storage()
        data = {'task': task, 'context': context}

        logger.log(f"Data:\n{data}", 'debug')

        prompt_formats = self.get_prompt_formats(data)
        print(f"\nExecution Agent Prompt: {prompt_formats}\nFeedback: {feedback}\n")
        prompt = self.generate_prompt(prompt_formats, feedback, context)
        with self.agent_funcs.thinking():
            result = self.execute_task(prompt)

        self.save_results(result)

        self.agent_funcs.stop_thinking()

        self.agent_funcs.print_result(result)

        logger.log(f"Agent Done!", 'info')
        return result

    def load_data_from_storage(self):
        task_list = self.storage.load_collection({
            'collection_name': "tasks",
            'collection_property': "documents"
        })

        task = task_list[0]

        return {'task': task}

    def get_prompt_formats(self, data):
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'context': data['context']},
            'InstructionPrompt': {'task': data['task']}
        }

        return prompt_formats

    def generate_prompt(self, prompt_formats, feedback="", context=""):
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']
        feedback_prompt = self.agent_data['prompts']['FeedbackPrompt'] if feedback != "" else ""

        # Format Prompts
        system_prompt = system_prompt.format(**prompt_formats.get('SystemPrompt', {}))
        context_prompt = context_prompt.format(context=context)
        instruction_prompt = instruction_prompt.format(**prompt_formats.get('InstructionPrompt', {}))
        feedback_prompt = feedback_prompt.format(feedback=feedback)

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{context_prompt}{instruction_prompt}{feedback_prompt}"}
        ]

        logger.log(f"Prompt:\n{prompt}", 'debug')
        return prompt

    def execute_task(self, prompt):
        return self.agent_data['generate_text'](prompt, self.agent_data['model'], self.agent_data['params']).strip()

    def save_results(self, result):
        self.storage.save_results({'result': result, 'collection_name': "results"})

