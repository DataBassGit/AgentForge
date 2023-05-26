from .func.agent_functions import AgentFunctions
from ..logs.logger_config import Logger


class Agent:
    def __init__(self, agent_name, log_level="debug"):
        self.agent_funcs = AgentFunctions(agent_name)
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils
        self.logger = Logger(name=agent_name)
        self.logger.set_level(log_level)

    def run(self, *args, **kwargs):
        pass

    def order_tasks(self, task_collection):
        # Pair up 'ids', 'documents' and 'metadatas' for sorting
        paired_up_tasks = list(zip(task_collection['ids'], task_collection['documents'], task_collection['metadatas']))

        # Sort the paired up tasks by 'task_order' in 'metadatas'
        sorted_tasks = sorted(paired_up_tasks, key=lambda x: x[2]['task_order'])

        # Split the sorted tasks back into separate lists
        sorted_ids, sorted_documents, sorted_metadatas = zip(*sorted_tasks)

        # Create the ordered results dictionary
        ordered_list = {
            'ids': list(sorted_ids),
            'embeddings': task_collection['embeddings'],  # this remains the same as it was not sorted
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

    def get_prompt_formats(self, data):
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'context': data['context']},
            'InstructionPrompt': {'task': data['task']}
        }

        return prompt_formats

    def generate_prompt(self, prompt_formats, feedback="", context=""):
        # Load Prompts from Persona Data
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']
        feedback_prompt = self.agent_data['prompts'].get('FeedbackPrompt', "")

        # Format Prompts
        system_prompt = system_prompt.format(
            **prompt_formats.get('SystemPrompt', {})
        )
        context_prompt = context_prompt.format(
            **prompt_formats.get('ContextPrompt', {"context": context})
        )
        instruction_prompt = instruction_prompt.format(
            **prompt_formats.get('InstructionPrompt', {})
        )
        feedback_prompt = feedback_prompt.format(
            **prompt_formats.get('FeedbackPrompt', {"feedback": feedback})
        )
        user_prompt = "".join((context_prompt, instruction_prompt, feedback_prompt))

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
