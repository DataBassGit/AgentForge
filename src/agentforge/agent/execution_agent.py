from .agent import Agent


class ExecutionAgent(Agent):

    def __init__(self):
        super().__init__('ExecutionAgent', log_level='info')

    def load_data_from_memory(self):
        task_list = self.storage.load_collection({
            'collection_name': "tasks",
            'collection_property': "documents"
        })
        task = task_list[0]
        return {'task': task}
