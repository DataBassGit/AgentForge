from agentforge.modules.ActionExecution import Action
from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent
from agentforge.agents.ExecutionAgent import ExecutionAgent
from agentforge.agents.TaskCreationAgent import TaskCreationAgent
from agentforge.agents.StatusAgent import StatusAgent
from agentforge.agents.SummarizationAgent import SummarizationAgent
from agentforge.logs.logger_config import Logger
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface


class Salience:

    def __init__(self):
        self.logger = Logger(name="Salience")

        self.data = {}
        self.task = {}
        self.context = {}
        self.feedback = {}
        self.reason = {}
        self.selected_action = {}

        self.frustration_step = 0.1
        self.min_frustration = 0.9
        self.max_frustration = 1
        self.frustration = self.min_frustration

        self.storage = StorageInterface().storage_utils
        self.functions = Functions()

        self.summarization_agent = SummarizationAgent()
        self.action_execution = Action()
        self.action_selection = ActionSelectionAgent()
        self.exec_agent = ExecutionAgent()
        self.task_creation_agent = TaskCreationAgent()
        self.status_agent = StatusAgent()

        self.init_settings_and_objectives()

    def init_settings_and_objectives(self):
        self.action_selection.set_threshold(self.frustration)
        self.action_selection.set_number_of_results(10)
        self.set_objective()

    def run(self):
        self.log_start()
        self.load_data_from_storage()
        self.summarize_task()
        self.check_for_actions()
        self.log_results()

    def loop(self):
        while True:
            self.display_task_list()
            self.fetch_context()
            self.fetch_feedback()
            self.run()
            self.determine_status()
            self.handle_frustration()

    def check_for_actions(self):
        self.select_action()

        if self.selected_action:
            self.execute_action()
        else:
            self.execute_task()

    def execute_action(self):
        action_results = self.action_execution.run(action=self.selected_action, context=self.reason)
        formatted_results = self.format_action_results(action_results)

        self.task['execution_results'] = {
            "task_result": formatted_results,
            "current_task": self.data['current_task'],
            "context": self.context,
            "Order": self.data['Order']
        }

    @staticmethod
    def format_action_results(action_results):
        formatted_strings = []
        for key, value in action_results.items():
            formatted_string = f"{key}: {value}\n\n---\n"
            formatted_strings.append(formatted_string)

        return "\n".join(formatted_strings).strip('---\n')

    @staticmethod
    def get_feedback_from_status_results(status):
        if status is not None:
            completed = status['status']

            if 'not completed' in completed:
                result = status['reason']
            else:
                result = None

            return result

    def select_action(self):
        self.selected_action = None
        self.selected_action = self.action_selection.run(feedback=self.feedback)

        if self.selected_action:
            result = f"{self.selected_action['Name']}: {self.selected_action['Description']}"
            self.functions.printing.print_result(result, 'Action Selected')

    def determine_current_task(self):
        self.data['current_task'] = self.functions.task_handling.get_current_task()
        if self.data['current_task'] is None:
            self.logger.log("Task list has been completed!!!", 'info')
            quit()

    def determine_status(self):
        self.task['status_result'] = self.status_agent.run(**self.task['execution_results'])
        self.display_status_result()

    def display_status_result(self):
        status = self.task['status_result']['status']
        reason = self.task['status_result']['reason']
        result = f"Status: {status}\n\nReason: {reason}"
        self.functions.printing.print_result(result, 'Status Result')

    def display_execution_results(self):
        task_result = self.task['execution_results']['task_result']
        self.functions.printing.print_result(task_result, "Execution Results")

    def display_task_list(self):
        self.functions.task_handling.show_task_list('Salience')

    def execute_task(self):
        task_result = self.exec_agent.run(summary=self.data['summary'],
                                          context=self.context,
                                          feedback=self.feedback)

        self.task['execution_results'] = {
            "task_result": task_result,
            "current_task": self.data['current_task'],
            "context": self.context,
            "Order": self.data['Order']
        }

        self.display_execution_results()

    def fetch_ordered_task_list(self):
        self.data['ordered_list'] = self.functions.task_handling.get_ordered_task_list()

    def fetch_context(self):
        self.context = self.get_feedback_from_status_results(self.task.get('status_result'))

    def fetch_feedback(self):
        self.feedback = self.functions.user_interface.get_user_input()

    # noinspection PyTypeChecker
    def frustrate(self):
        if self.frustration < self.max_frustration:
            self.frustration += self.frustration_step
            self.frustration = min(self.frustration, self.max_frustration)
            self.action_selection.set_threshold(self.frustration)
            print("\nIncreased Frustration Level!")
        else:
            print(f"\nMax Frustration Level Reached: {self.frustration}")

    def handle_frustration(self):
        self.reason = None
        status = self.task['status_result']['status']
        self.reason = self.task['status_result']['reason']
        if status != 'completed':
            self.frustrate()
        else:
            self.frustration = self.min_frustration
            self.action_selection.set_threshold(self.frustration)

    def load_data_from_storage(self):
        self.load_results()
        self.fetch_ordered_task_list()
        self.determine_current_task()
        self.prepare_ordered_results()

    def load_results(self):
        results = self.storage.load_collection({'collection_name': "Results", 'include': ["documents"]})
        self.data['result'] = results['documents'][0] if results['documents'] else "No results found"

    def log_results(self):
        self.logger.log(f"Execution Results: {self.task['execution_results']}", 'debug')
        self.logger.log(f"Agent Done!", 'info')

    def log_start(self):
        self.logger.log(f"Running Agent ...", 'info')

    def prepare_ordered_results(self):
        self.data['task_ids'] = self.data['ordered_list']['ids']
        self.data['Order'] = self.data['current_task']["metadata"]["Order"]

    def set_objective(self):
        objective = self.functions.agent_utils.prepare_objective()
        if objective is not None:
            self.task_creation_agent.run()

    def summarize_task(self):
        task = self.data['current_task']['document']
        self.data['summary'] = self.summarization_agent.run(query=task)
        if self.data['summary'] is not None:
            self.functions.printing.print_result(result=self.data['summary'], desc="Summary Agent results")
        return self.data['summary']


if __name__ == '__main__':
    Salience().loop()
