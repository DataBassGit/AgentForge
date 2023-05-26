from .agent import Agent
from .execution_agent import ExecutionAgent
from .summarization_agent import SummarizationAgent


class SalienceAgent(Agent):
    def __init__(self):
        super().__init__('SalienceAgent', log_level="info")

        # Summarize the Search Results
        self.summarization_agent = SummarizationAgent()
        self.exec_agent = ExecutionAgent()

    def run(self, feedback=None):

        self.logger.log(f"Running Agent...", 'info')
        # Load Last Results and Current Task as Data
        data = self.load_data_from_storage()

        # Feed Data to the Search Utility
        search_results = self.storage.query_db("results", data['current_task']['document'], 5)['documents']

        self.logger.log(f"Search Results: {search_results}", 'info')

        # Summarize the Search Results
        if search_results == 'No Results!':
            context = "No previous actions have been taken."
        else:
            context = self.summarization_agent.run_summarization_agent(search_results)

        # self.logger.log(f"Summary of Results: {context}", 'info')

        task_result = self.exec_agent.run_execution_agent(context=context, feedback=feedback)

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

        self.logger.log(f"Execution Results: {execution_results}", 'debug')

        self.logger.log(f"Agent Done!", 'info')
        return execution_results

    def load_data_from_storage(self):
        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'collection_property': "documents"
        })
        result = result_collection[0] if result_collection else ["No results found"]

        self.logger.log(f"Load Data Results:\n{result}", 'debug')

        task_collection = self.storage.load_salient({
            'collection_name': "tasks",
            'collection_property': ["documents", "metadatas"],
            'ids': "ids"
        })

        self.logger.log(f"Tasks Before Ordering:\n{task_collection}", 'debug')
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

        self.logger.log(f"Tasks Ordered list:\n{ordered_list}", 'debug')

        self.logger.log(f"Tasks IDs:\n{sorted_ids}", 'debug')

        current_task = None
        # iterate over sorted_metadatas
        for i, metadata in enumerate(sorted_metadatas):
            # check if the task_status is not completed
            self.logger.log(f"Sorted Metadatas:\n{metadata}", 'debug')
            if metadata['task_status'] == 'not completed':
                current_task = {
                    'id': sorted_ids[i],
                    'document': sorted_documents[i],
                    'metadata': metadata
                }
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
            'task_order': current_task["metadata"]["task_order"]
        }

        return ordered_results
