import uuid

from .. import config


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
            storage_api = config.storage_api()
            if storage_api == 'chroma':
                self.initialize_chroma()
            else:
                raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def initialize_chroma(self):
        from .chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()
        self.storage_utils.init_storage()
        self.storage_utils.select_collection("results")
        self.storage_utils.select_collection("tasks")

        if config.get('ChromaDB', 'DBFreshStart') == 'True':
            collection_name = "tasks"
            self.storage_utils.clear_collection(collection_name)

            persona_data = config.persona()
            task_dicts = [{"task_order": i + 1, "task_desc": task}
                          for i, task in enumerate(persona_data['Tasks'])]
            task_list = [task_dict["task_desc"] for task_dict in task_dicts]

            metadatas = [{
                "task_status": "not completed",
                "task_desc": task["task_desc"],
                "list_id": str(uuid.uuid4()),
                "task_order": task["task_order"]
            } for task in task_dicts]

            params = {
                "collection_name": collection_name,
                "ids": [str(order["task_order"]) for order in task_dicts],
                "data": task_list,
                "metadata": metadatas,
            }
            self.storage_utils.save_memory(params)