from .func.agent_functions import AgentFunctions
from ..logs.logger_config import Logger


class Agent:
    def __init__(self, agent_name, log_level="debug"):
        self.agent_funcs = AgentFunctions(agent_name)
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils
        self.logger = Logger(name=agent_name)
        self.logger.set_level(log_level)

    def run(self, **kwargs):
        # This function will be the main entry point for your agent.
        self.logger.log(f"Running Agent...", 'info')

        # Load data
        data = {}
        if "database" in self.agent_data:
            db_data = self.load_data_from_memory()
            data.update(db_data)
        data.update(self.agent_data)
        data.update(kwargs)

        # Generate prompt
        prompt = self.generate_prompt(**data)

        # Execute the main task of the agent
        with self.agent_funcs.thinking():
            result = self.execute_task(prompt)

        # Save the results
        self.save_results(result)

        # Stop Console Feedback
        self.agent_funcs.stop_thinking()

        # Print the result or any other relevant information
        self.agent_funcs.print_result(result)

        self.logger.log(f"Agent Done!", 'info')

    def order_tasks(self, task_collection):
        # Pair up 'ids', 'documents' and 'metadatas' for sorting
        paired_up_tasks = list(zip(task_collection['ids'], task_collection['documents'],
                                   task_collection['metadatas']))

        # Sort the paired up tasks by 'task_order' in 'metadatas'
        sorted_tasks = sorted(paired_up_tasks, key=lambda x: x[2]['task_order'])

        # Split the sorted tasks back into separate lists
        sorted_ids, sorted_documents, sorted_metadatas = zip(*sorted_tasks)

        # Create the ordered results dictionary
        ordered_list = {
            'ids': list(sorted_ids),
            'embeddings': task_collection['embeddings'],
            # this remains the same as it was not sorted
            'documents': list(sorted_documents),
            'metadatas': list(sorted_metadatas),
        }

        self.logger.log(f"Tasks Ordered list:\n{ordered_list}", 'debug')

        return ordered_list, sorted_ids, sorted_documents, sorted_metadatas

    # def load_task_data(self):
    #     task_collection = self.storage.load_salient({
    #         'collection_name': "tasks",
    #         'collection_property': ["documents", "metadatas"],
    #         'ids': "ids"
    #     })
    #
    #     ordered_list, sorted_ids, sorted_documents, sorted_metadatas = self.order_tasks(task_collection)
    #
    #     current_task = None
    #     # iterate over sorted_metadatas
    #     for i, metadata in enumerate(sorted_metadatas):
    #         # check if the task_status is not completed
    #         self.logger.log(f"Sorted Metadatas:\n{metadata}", 'debug')
    #         if metadata['task_status'] == 'not completed':
    #             current_task = {
    #                 'id': sorted_ids[i],
    #                 'document': sorted_documents[i],
    #                 'metadata': metadata
    #             }
    #             break  # break the loop as soon as we find the first not_completed task
    #
    #     if current_task is None:
    #         self.logger.log("Task list has been completed!!!", 'info')
    #         quit()
    #
    #     self.logger.log(f"Current Task:{current_task['document']}", 'info')
    #     self.logger.log(f"Current Task:\n{current_task}", 'debug')
    #
    #     result = None
    #
    #     ordered_results = {
    #         'result': result,
    #         'current_task': current_task,
    #         'task_list': ordered_list,
    #         'task_ids': sorted_ids,
    #         'task_order': current_task["metadata"]["task_order"]
    #     }
    #
    #     return ordered_results

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
