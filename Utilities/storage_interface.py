import configparser
from Personas.load_persona_data import load_persona_data

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
storage_api = config.get('StorageAPI', 'library')
persona_data = load_persona_data()
task_list = persona_data['Tasks']
task_dicts = [{"task_order": i + 1, "task_desc": task} for i, task in enumerate(task_list)]
task_list = [task_dict["task_desc"] for task_dict in task_dicts]

# for task_dict in task_dicts:
    # print("Task: ", task_dict["task_desc"])

# print("\nTasks: ", task_list)


class StorageInterface:
    _instance = None
    storage_utils = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StorageInterface, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialize_storage()
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        pass

    def initialize_storage(self):
        if self.storage_utils is None:
            if storage_api == 'chroma':
                self.initialize_chroma()
            else:
                raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def initialize_chroma(self):
        from Utilities.chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()
        self.storage_utils.init_storage()
        self.storage_utils.select_collection("results")
        self.storage_utils.select_collection("tasks")

        inject = input("Restore previous state? (y/n):")

        if inject == 'n':
            self.storage_utils.client.reset()
            self.storage_utils.select_collection("results")
            self.storage_utils.select_collection("tasks")
            self.storage_utils.save_tasks({'tasks': task_dicts, 'results': task_list, 'collection_name': "tasks"})
