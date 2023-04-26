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
            print(f"Current Task: {data['task'][0]}")

            # Feed Data to the Search Utility
            search_results = self.storage.query_db("results", data['task'][0], 5)['documents']
            # print(f"Search Results: {search_results}")
            # quit()

            # Summarize the Search Results
            if search_results == 'No Results!':
                context = "No previous actions have been taken."
            else:
                context = self.summarization_agent.run_summarization_agent(search_results)
                # print(f"\nSummary of Results: {context}")

            task_result = self.exec_agent.run_execution_agent(context=context, feedback=None)

            # Feed the Summarized Results and the Current Task to the Job Agent

            # Feed the Job Agent Results to the Execution Agent

            # Return Execution Results to the Job Agent to determine Frustration

            # Depending on Frustration Results feed the Tasks and Execution Results to the Analysis Agent to determine the status of the Current Task
            #Anaglist Agent
            # Save the Status of the task to the Tasks DB
            return {
                "task_result": task_result,
                "current_task": data['task'],
                "context": context,
                "task_order": data['task_order']
            }

    def load_data_from_storage(self):
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]

        task_collection = self.storage.load_salient({
            'collection_name': "tasks",
            'collection_property': ["documents", "metadatas"],
            'ids': "ids"
        })
        # print(f"\n\nSalience Agent - Tasks: {task_collection}")


        # ... (previous code)
        task_collection = self.storage.load_salient({
            'collection_name': "tasks",
            'collection_property': ["documents", "metadatas"],
            'ids': "ids"
        })

        print(f"\n\nSalience Agent - Tasks ybefore ordering:\n\n {task_collection}\n\n")

        if task_collection:
            merged_task_list = [
                {"document": doc, "metadata": metadata}
                for doc, metadata in zip(task_collection["documents"], task_collection["metadatas"])
            ]
            task_list = sorted(
                merged_task_list,
                key=lambda x: x["metadata"]["task_order"]
            )
        else:
            task_list = []
        task_ids = task_collection["ids"] if task_collection else []  # Added this line to get the task IDs
        task = (task_list[0]["document"], task_ids[0]) if task_list and task_ids else (
        None, None)  # Modified to include task ID
        print(f"\n Task List: {task_list}, Task IDs: {task_ids}, Task: {task}")
        ordered_results = {'result': result, 'task': task, 'task_list': task_list, 'task_ids': task_ids, 'task_order': task_list[0]["metadata"]["task_order"]}

        return ordered_results

        # if task_collection:
        #     print("\n\nSalience Agent - Tasks Debug:\n\n")
        #     print(task_collection["documents"])
        #
        #     for document in task_collection["documents"]:
        #         print(document["metadatas"])
        #
        #     task_list = sorted(
        #         task_collection["documents"],
        #         key=lambda x: [metadata["task_order"] for metadata in x["metadatas"]]
        #     )
        # else:
        #     task_list = []
        # task_ids = task_collection["ids"] if task_collection else []  # Added this line to get the task IDs
        # task = (task_list[0], task_ids[0]) if task_list and task_ids else (None, None)  # Modified to include task ID
        # print(f"\n Task List: {task_list}, Task IDs: {task_ids}, Task: {task}")
        # ordered_results = {'result': result, 'task': task, 'task_list': task_list, 'task_ids': task_ids}
        #
        # return ordered_results

    def get_prompt_formats(self, data):
        # Create a dictionary of prompt formats based on the loaded data
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'context': data['context']},
            'InstructionPrompt': {'task': data['task']}
        }
        return prompt_formats

    def generate_prompt(self, prompt_formats, feedback=None):
        # Generate the prompt using prompt_formats and return it.
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

