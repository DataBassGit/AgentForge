from agentforge.agent.ExecutionAgent import ExecutionAgent
from agentforge.agent.StatusAgent import StatusAgent
from agentforge.agent.SummarizationAgent import SummarizationAgent
from agentforge.logs.logger_config import Logger
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface


class Salience:
    def __init__(self):
        # Summarize the Search Results
        self.summarization_agent = SummarizationAgent()
        self.exec_agent = ExecutionAgent()
        self.status_agent = StatusAgent()
        self.storage = StorageInterface().storage_utils
        self.logger = Logger(name="Salience")
        self.functions = Functions()

        log_tasks = self.functions.show_task_list('Objectives')
        filename = "../../../Examples/Architectures/Logs/results.txt"
        with open(filename, "a") as file:
            file.write(log_tasks)

    def run(self, feedback=None):

        self.logger.log(f"Running Agent...", 'info')
        # Load Last Results and Current Task as Data
        data = self.load_data_from_storage()

        # Feed Data to the Search Utility
        params = {'collection_name': "Results", 'query': data['current_task']['document']}
        search_results = self.storage.query_memory(params, 5)['documents']

        self.logger.log(f"Search Results: {search_results}", 'info')

        # Summarize the Search Results
        if search_results == 'No Results!':
            context = None
        else:
            context = self.summarization_agent.run()
            self.functions.print_result(result=context['result'], desc="Summary Agent results")

        # self.logger.log(f"Summary of Results: {context}", 'info')

        task_result = self.exec_agent.run()

        # Return Execution Results to the Job Agent to determine Frustration

        # Depending on Frustration Results feed the Tasks and Execution Results
        # to the Analysis Agent to determine the status of the Current Task

        # Save the Status of the task to the Tasks DB

        execution_results = {"task_result": task_result,
                             "current_task": data['current_task'],
                             "context": context,
                             "Order": data['Order']}

        self.logger.log(f"Execution Results: {execution_results}", 'debug')

        self.logger.log(f"Agent Done!", 'info')
        return execution_results

    def load_data_from_storage(self):
        result_collection = self.storage.load_collection({'collection_name': "Results", 'include': ["documents"]})

        if result_collection['documents']:
            result = result_collection['documents'][0]
        else:
            result = "No results found"

        self.logger.log(f"Load Data Results:\n{result}", 'debug')

        task_collection = self.storage.load_collection({'collection_name': "Tasks",
                                                        'include': ["documents", "metadatas"]})

        self.logger.log(f"Tasks Before Ordering:\n{task_collection}", 'debug')
        # quit()

        # first, pair up 'ids', 'documents' and 'metadatas' for sorting
        paired_up_tasks = list(zip(task_collection['ids'], task_collection['documents'], task_collection['metadatas']))

        # sort the paired up tasks by 'Order' in 'metadatas'
        sorted_tasks = sorted(paired_up_tasks, key=lambda x: x[2]['Order'])

        # split the sorted tasks back into separate lists
        sorted_ids, sorted_documents, sorted_metadatas = zip(*sorted_tasks)

        # create the ordered results dictionary
        ordered_list = {
            'ids': list(sorted_ids),
            'embeddings': task_collection['embeddings'],
            # this remains the same as it was not sorted
            'documents': list(sorted_documents),
            'metadatas': list(sorted_metadatas),
        }

        self.logger.log(f"Tasks Ordered list:\n{ordered_list}", 'debug')
        self.logger.log(f"Tasks IDs:\n{sorted_ids}", 'debug')

        current_task = None
        # iterate over sorted_metadatas
        for i, metadata in enumerate(sorted_metadatas):
            # check if the Task Status is not completed
            self.logger.log(f"Sorted Metadatas:\n{metadata}", 'debug')
            if metadata['Status'] == 'not completed':
                current_task = {'id': sorted_ids[i], 'document': sorted_documents[i], 'metadata': metadata}
                break  # break the loop as soon as we find the first not_completed task

        if current_task is None:
            self.logger.log("Task list has been completed!!!", 'info')
            quit()

        self.logger.log(f"Current Task:{current_task['document']}", 'info')
        self.logger.log(f"Current Task:\n{current_task}", 'debug')

        ordered_results = {
            'result': result,
            'current_task': current_task,
            'task_list': ordered_list,
            'task_ids': sorted_ids,
            'Order': current_task["metadata"]["Order"]
        }

        return ordered_results

    def loop(self):
        # Add a variable to set the mode
        self.functions.user_interface.set_auto_mode()
        status = None

        while True:
            collection_list = self.storage.collection_list()
            self.logger.log(f"Collection List: {collection_list}", 'debug')

            # Allow for feedback if auto mode is disabled
            status_result = self.functions.get_feedback_from_status_results(status)
            if status_result is not None:
                feedback = self.functions.get_user_input(status_result)
            else:
                feedback = self.functions.get_user_input()

            data = self.run(feedback=feedback)

            self.logger.log(f"Data: {data}", 'debug')
            self.functions.print_result(data['task_result']['result'], "Execution Results")
            status = self.status_agent.run()

            result = f"Status: {status['status']}\n\nReason: {status['reason']}"

            self.functions.print_result(result, 'Status Agent')

            self.functions.show_task_list('Salience')


if __name__ == '__main__':
    Salience().loop()
