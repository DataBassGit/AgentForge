from Agents.Func.agent_functions import AgentFunctions
from Agents.summarization_agent import SummarizationAgent
from Agents.execution_agent import ExecutionAgent

class SalienceAgent:
    agent_data = None
    agent_funcs = None
    storage = None
    spinner_thread = None

    def __init__(self):
        self.agent_funcs = AgentFunctions('SalienceAgent')
        self.agent_data = self.agent_funcs.agent_data
        self.storage = self.agent_data['storage'].storage_utils

    def run_salience_agent(self, feedback=None):
        # 1. Start Console Feedback
        with self.agent_funcs.thinking():
            # Load Last Results and Current Task as Data
            data = self.load_data_from_storage()
            print(f"Current Task: {data['task']}")

            # Feed Data to the Search Utility
            search_results = self.storage.query_db("results", data['task'], 5)['documents']
            # print(search_results)
            # quit()
            # Summarize the Search Results
            summarizationAgent = SummarizationAgent()
            summarized_results = summarizationAgent.run_summarization_agent(search_results)
            # print(f"\nSummary of Results: {summarized_results}")
            exec_agent = ExecutionAgent()
            exec_results = exec_agent.run_execution_agent(context=summarized_results, feedback=None)

            # Feed the Summarized Results and the Current Task to the Job Agent

            # Feed the Job Agent Results to the Execution Agent

            # Return Execution Results to the Job Agent to determine Frustration

            # Depending on Frustration Results feed the Tasks and Execution Results to the Analysis Agent to determine the status of the Current Task

            # Save the Status of the task to the Tasks DB
            return exec_results

        # # 2. Load data from storage
        # data = self.load_data_from_storage()
        #
        # # 3. Get prompt formats
        # prompt_formats = self.get_prompt_formats(data)
        #
        # # 4. Generate prompt
        # prompt = self.generate_prompt(prompt_formats, feedback)
        #
        # # 5. Execute the main task of the agent
        # result = self.execute_task(prompt)
        #
        # # 6. Save the results
        # self.save_results(result)
        #
        # # 7. Stop Console Feedback
        # self.agent_funcs.stop_thinking()
        #
        # # 8. Print the result or any other relevant information
        # self.agent_funcs.print_result(result)

    def load_data_from_storage(self):
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]

        task_collection = self.storage.load_collection({
            'collection_name': "tasks",
            'collection_property': "documents"
        })

        task_list = task_collection if task_collection else []
        task = task_list[0] if task_collection else None

        return {'result': result, 'task': task, 'task_list': task_list}
        pass

    def get_prompt_formats(self, data):
        # Create a dictionary of prompt formats based on the loaded data
        prompt_formats = {
            'SystemPrompt': {'objective': self.agent_data['objective']},
            'ContextPrompt': {'context': data['context']},
            'InstructionPrompt': {'task': data['task']}
        }
        return prompt_formats
    pass

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
        pass

    def execute_task(self, prompt):
        # Execute the main task of the agent and return the result
        pass

    def save_results(self, result):
        # Save the results to storage
        pass

