import configparser
from Personas.load_persona_data import load_persona_data

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
storage_api = config.get('StorageAPI', 'library')
persona_data = load_persona_data('Personas/default.json')
task_list = persona_data['Tasks']
task_dicts = [{"task_order": i + 1, "task_desc": task} for i, task in enumerate(task_list)]
for task_dict in task_dicts:
    print("Task: ", task_dict["task_desc"])
task_descs = [task_dict["task_desc"] for task_dict in task_dicts]
print("\nTasks: ", task_descs)



class StorageInterface:
    _instance = None

    storage_utils = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(StorageInterface, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        self.initialize_storage()
        pass

    def initialize_storage(self):
        print("Initializing storage...")
        if storage_api == 'chroma':
            storage = "tasks"
            from Utilities.chroma_utils import ChromaUtils
            self.storage_utils = ChromaUtils()
            try:
                self.storage_utils.select_collection(storage)
                self.storage_utils.save_tasks(task_dicts, task_descs, "tasks")
            except Exception as e:
                print("Error during upsert:", e, "\nCreating table... Name: tasks")
                self.storage_utils.create_storage(storage)
                print("\nPersona data: ", task_dicts)
                self.storage_utils.save_tasks(task_dicts, task_descs, "tasks")

                print("Table created!")
                print(self.storage_utils.get_collection().get())
        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")

        # Initialize Chroma
        self.storage_utils.init_storage()

        return self.storage_utils

    def get_storage(self):
        if storage_api == 'chroma':
            return self.storage_utils.get_collection()

        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def get_task(self):
        pass
    def sel_collection(self,name):
        self.storage_utils.select_collection(name)
    def get_result(self, task):
        result = self.storage_utils.get_collection().query(
            query_texts=[task["task_desc"]],
            n_results=1
        )

        return result

    def get_results(self, task):
        result = self.storage_utils.get_collection().query(
            query_texts=[task["task_desc"]],
            n_results=1
        )

        return result

    def save_tasks(self, tasks, results, collection_name):
        if storage_api == 'chroma':
            self.storage_utils.save_tasks(tasks, results, collection_name)
        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def create_col(self, collection):
        if storage_api == 'chroma':
            self.storage_utils.create_storage(collection)
        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def list_col(self):
        if storage_api == 'chroma':
            return self.storage_utils.list_collections()
        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def save_results(self, results, collection_name):
        if storage_api == 'chroma':
            self.storage_utils.save_results(results, collection_name)
        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")