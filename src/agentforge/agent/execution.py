from .agent import Agent


class ExecutionAgent(Agent):
    def load_data_from_memory(self):
        task_list = self.storage.load_collection({
            'collection_name': "tasks",
            'include': ["documents"],
        })
        task = task_list['documents'][0]
        return {'task': task}
