import configparser

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
storage_api = config.get('StorageAPI', 'library')


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
        if storage_api == 'chroma':
            from Utilities.chroma_utils import ChromaUtils
            self.storage_utils = ChromaUtils()

        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")

        # Initialize Chroma
        self.storage_utils.init_storage()

        # Create Pinecone index
        self.storage_utils.create_storage()

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

    def save_results(self, tasks, results):
        if storage_api == 'chroma':
            self.storage_utils.save_tasks(tasks, results)
            # print(self.get_result(tasks))
        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def create_col(self, collection):
        if storage_api == 'chroma':
            self.storage_utils.create_storage(collection)
        else:
            raise ValueError(f"Unsupported Storage API library: {storage_api}")