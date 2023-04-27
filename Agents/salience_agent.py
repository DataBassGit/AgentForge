from Agents.Func.agent_functions import AgentFunctions
from Agents.summarization_agent import SummarizationAgent
from Agents.execution_agent import ExecutionAgent


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

    def run_salience_agent(self, feedback=None):
        # 1. Start Console Feedback
        with self.agent_funcs.thinking():
            # Load Last Results and Current Task as Data
            data = self.load_data_from_storage()
            print(f"\n\nCurrent Task: {data['current_task']}")

            # Feed Data to the Search Utility
            search_results = self.storage.query_db("results", data['current_task']['document'], 5)['documents']
            print(f"\n\nSearch Results: {search_results}")
            # quit()

            # Summarize the Search Results
            if search_results == 'No Results!':
                context = "No previous actions have been taken."
            else:
                context = self.summarization_agent.run_summarization_agent(search_results)

            print(f"\n\nSummary of Results: {context}")

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

            print(f"\n\nSalience - Execution Results: {execution_results}")

            return execution_results

    def load_data_from_storage(self):
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]

        # print(f"\nSalience Load Data Results: {result}")
        # quit()

        task_collection = self.storage.load_salient({
            'collection_name': "tasks",
            'collection_property': ["documents", "metadatas"],
            'ids': "ids"
        })

        print(f"\n\nSalience Agent - Tasks before ordering:\n{task_collection}")
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

        print(f"\n\nSalience Agent - Tasks Ordered list:\n{ordered_list}")

        print(f"\n\nSalience Agent - Tasks IDs:\n{sorted_ids}\n")

        current_task = None
        # iterate over sorted_metadatas
        for i, metadata in enumerate(sorted_metadatas):
            # check if the task_status is not completed
            print(f"\nSalience Agent - Sorted Metadatas:\n{metadata}")
            if metadata['task_status'] == 'not completed':
                current_task = {
                    'id': sorted_ids[i],
                    'document': sorted_documents[i],
                    'metadata': metadata
                }
                break  # break the loop as soon as we find the first not_completed task

        print(f"\n\nSalience Agent - Current Task:\n{current_task}")

        if current_task == None:
            print("\n\nTask list has been completed!!!")

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

