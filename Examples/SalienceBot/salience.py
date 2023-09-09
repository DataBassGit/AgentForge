from agentforge.loops.ActionExecution import Action
from agentforge.agents.ExecutionAgent import ExecutionAgent
from agentforge.agents.TaskCreationAgent import TaskCreationAgent
from agentforge.agents.StatusAgent import StatusAgent
from agentforge.agents.SummarizationAgent import SummarizationAgent
from agentforge.logs.logger_config import Logger
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface


class Salience:

    def __init__(self):
        # Summarize the Search Results
        self.summarization_agent = SummarizationAgent()
        self.action = Action()
        self.exec_agent = ExecutionAgent()
        self.task_creation_agent = TaskCreationAgent()
        self.status_agent = StatusAgent()
        self.storage = StorageInterface().storage_utils
        self.logger = Logger(name="Salience")
        self.functions = Functions()

        self.data = {}

        self.frustration = 0
        self.frustration_step = 0.1
        self.max_frustration = 0.5

        self.set_objective()

    def run(self, context=None, feedback=None):
        self.log_start()
        self.load_data_from_storage()
        summary = self.summarize_task(self.data['current_task']['document'])
        execution_results = self.execute_task(summary, context, feedback, self.data)
        self.log_results(execution_results)
        return execution_results

    def loop(self):
        status_results = None
        while True:
            self.display_task_list()
            status_result, feedback = self.fetch_status_and_feedback(status_results)
            data = self.run_agent(status_result, feedback)
            self.display_execution_results(data['task_result'])
            status_results = self.determine_status(data)
            self.handle_frustration(data['status'], data['reason'])

    def determine_current_task(self):
        self.data['current_task'] = self.functions.get_current_task()
        if self.data['current_task'] is None:
            self.logger.log("Task list has been completed!!!", 'info')
            quit()

    def determine_status(self, data):
        status_results = self.status_agent.run(**data)
        data['status'] = status_results['status']
        data['reason'] = status_results['reason']
        result = f"Status: {data['status']}\n\nReason: {data['reason']}"
        self.functions.print_result(result, 'Status Result')
        return status_results

    def display_execution_results(self, task_result):
        self.functions.print_result(task_result, "Execution Results")

    def display_task_list(self):
        self.functions.show_task_list('Salience')

    def execute_task(self, summary, context, feedback, data):
        task_result = self.exec_agent.run(summary=summary, context=context, feedback=feedback)
        return {
            "task_result": task_result,
            "current_task": data['current_task'],
            "context": context,
            "Order": data['Order']
        }

    def fetch_ordered_task_list(self):
        self.data['ordered_list'] = self.functions.get_ordered_task_list()

    def fetch_status_and_feedback(self, status_results):
        status_result = self.functions.check_status(status_results)
        feedback = self.functions.check_auto_mode()
        return status_result, feedback

    # noinspection PyTypeChecker
    def frustrate(self):
        if self.frustration < self.max_frustration:
            self.frustration += self.frustration_step
            self.frustration = min(self.frustration, self.max_frustration)
            print("\nIncreased Frustration Level!")
        else:
            print(f"\nMax Frustration Level Reached: {self.frustration}")

    def handle_frustration(self, status, reason):
        if status != 'completed':
            self.frustrate()
            self.action.run(reason, frustration=self.frustration)
        else:
            self.frustration = 0

    def load_data_from_storage(self):
        self.load_results()
        self.fetch_ordered_task_list()
        self.determine_current_task()
        self.prepare_ordered_results()

    def load_results(self):
        results = self.storage.load_collection({'collection_name': "Results", 'include': ["documents"]})
        self.data['result'] = results['documents'][0] if results['documents'] else "No results found"

    def log_results(self, execution_results):
        self.logger.log(f"Execution Results: {execution_results}", 'debug')
        self.logger.log(f"Agent Done!", 'info')

    def log_start(self):
        self.logger.log(f"Running Agent ...", 'info')

    def prepare_ordered_results(self):
        self.data['task_ids'] = self.data['ordered_list']['ids']
        self.data['Order'] = self.data['current_task']["metadata"]["Order"]

    def run_agent(self, status_result, feedback):
        data = self.run(context=status_result, feedback=feedback)
        self.logger.log(f"Data: {data}", 'debug')
        return data

    def set_objective(self):
        objective = self.functions.prepare_objective()
        if objective is not None:
            self.task_creation_agent.run()

    def summarize_task(self, task_document):
        summary = self.summarization_agent.run(query=task_document)
        if summary is not None:
            self.functions.print_result(result=summary, desc="Summary Agent results")
        return summary


if __name__ == '__main__':
    Salience().loop()
