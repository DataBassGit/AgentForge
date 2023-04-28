from Agents.Func.agent_functions import AgentFunctions
from Agents.summarization_agent import SummarizationAgent
from Agents.execution_agent import ExecutionAgent
from Logs.logger_config import Logger

logger = Logger(name="Salience Agent")


class SalienceAgent:
    agent_data = None
    agent_funcs = None
    storage = None
    spinner_thread = None
    summarization_agent = None
    exec_agent = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('SalienceAgent')
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils

        # Summarize the Search Results
        self.summarization_agent = SummarizationAgent()
        self.exec_agent = ExecutionAgent()

        logger.set_level('info')

    def run_salience_agent(self, feedback=None):

        logger.log(f"Running Agent...", 'info')

        # Load Last Results and Current Task as Data
        data = self.load_data_from_storage()

        # Feed Data to the Search Utility
        search_results = self.storage.query_db("results", data['current_task']['document'], 5)['documents']

        logger.log(f"Search Results: {search_results}", 'info')

        # Summarize the Search Results
        if search_results == 'No Results!':
            context = "No previous actions have been taken."
        else:
            context = self.summarization_agent.run_summarization_agent(search_results)

        # logger.log(f"Summary of Results: {context}", 'info')

        task_result = self.exec_agent.run_execution_agent(context=context, feedback=None)

        # Return Execution Results to the Job Agent to determine Frustration

        # Depending on Frustration Results feed the Tasks and Execution Results to the Analysis Agent
        # to determine the status of the Current Task

        # Save the Status of the task to the Tasks DB

        execution_results = {
            "task_result": task_result,
            "current_task": data['current_task'],
            "context": context,
            "task_order": data['task_order']
        }

        logger.log(f"Execution Results: {execution_results}", 'debug')

        logger.log(f"Agent Done!", 'info')
        return execution_results

    def load_data_from_storage(self):
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]

        logger.log(f"Load Data Results:\n{result}", 'debug')

        task_collection = self.storage.load_salient({
            'collection_name': "tasks",
            'collection_property': ["documents", "metadatas"],
            'ids': "ids"
        })

        logger.log(f"Tasks Before Ordering:\n{task_collection}", 'debug')
        # quit()

        # first, pair up 'ids', 'documents' and 'metadatas' for sorting
        paired_up_tasks = list(zip(task_collection['ids'], task_collection['documents'], task_collection['metadatas']))

        # sort the paired up tasks by 'task_order' in 'metadatas'
        sorted_tasks = sorted(paired_up_tasks, key=lambda x: x[2]['task_order'])

        # split the sorted tasks back into separate lists
        sorted_ids, sorted_documents, sorted_metadatas = zip(*sorted_tasks)

        # create the ordered results dictionary
        ordered_list = {
            'ids': list(sorted_ids),
            'embeddings': task_collection['embeddings'],  # this remains the same as it was not sorted
            'documents': list(sorted_documents),
            'metadatas': list(sorted_metadatas),
        }

        logger.log(f"Tasks Ordered list:\n{ordered_list}", 'debug')

        logger.log(f"Tasks IDs:\n{sorted_ids}", 'debug')

        current_task = None
        # iterate over sorted_metadatas
        for i, metadata in enumerate(sorted_metadatas):
            # check if the task_status is not completed
            logger.log(f"Sorted Metadatas:\n{metadata}", 'debug')
            if metadata['task_status'] == 'not completed':
                current_task = {
                    'id': sorted_ids[i],
                    'document': sorted_documents[i],
                    'metadata': metadata
                }
                break  # break the loop as soon as we find the first not_completed task

        if current_task is None:
            logger.log("Task list has been completed!!!", 'info')
            quit()

        logger.log(f"Current Task:{current_task['document']}", 'info')
        logger.log(f"Current Task:\n{current_task}", 'debug')

        ordered_results = {
            'result': result,
            'current_task': current_task,
            'task_list': ordered_list,
            'task_ids': sorted_ids,
            'task_order': current_task["metadata"]["task_order"]
        }

        return ordered_results

    def get_prompt_formats(self, data):
        # Create a dictionary of prompt formats based on the loaded data
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'context': data['context']},
            'InstructionPrompt': {'task': data['task']}
        }
        return prompt_formats

    def generate_prompt(self, prompt_formats, feedback=None):
        # Load Prompts
        system_prompt = self.agent_data['prompts']['SystemPrompt']
        context_prompt = self.agent_data['prompts']['ContextPrompt']
        instruction_prompt = self.agent_data['prompts']['InstructionPrompt']
        feedback_prompt = self.agent_data['prompts']['FeedbackPrompt'] if feedback != "" else ""

        # Format Prompts
        system_prompt = system_prompt.format(**prompt_formats.get('SystemPrompt', {}))
        context_prompt = context_prompt.format(**prompt_formats.get('ContextPrompt', {}))
        instruction_prompt = instruction_prompt.format(**prompt_formats.get('InstructionPrompt', {}))
        feedback_prompt = feedback_prompt.format(feedback=feedback)

        prompt = [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{context_prompt}{instruction_prompt}{feedback_prompt}"}
        ]

        # print(f"\nPrompt: {prompt}")
        return prompt

    def execute_task(self, prompt):
        # Execute the main task of the agent and return the result
        pass

    def save_results(self, result):
        # Save the results to storage
        pass

    # def show_tasks(self, agent):
    #     print("")
    #     logger.log(f"Agent {agent}", 'info')
