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

    def initialize_task_collection(self):
        """
        Initializes the tasks collection with the data from persona.json.
        """
        collection_name = "tasks"

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

    def initialize_tool_collection(self):
        """
        Initializes the tools collection with the data from tools.json.
        """
        tools_data = config.tools()

        metadatas = [{
            'Name': name,
            'Description': details['Description'],
            'Example': details['Example'],
            'Instruction': details['Instruction']}
            for name, details in tools_data.items()]

        ids = [str(i + 1) for i in range(len(tools_data))]
        tool_names = [metadata['Name'] for metadata in metadatas]

        params = {
            "collection_name": 'Tools',
            "ids": ids,
            "data": tool_names,
            "metadata": metadatas,
        }

        self.storage_utils.save_memory(params)

    def initialize_chroma(self):
        from .chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()
        self.storage_utils.init_storage()
        self.storage_utils.select_collection("results")
        self.storage_utils.select_collection("tasks")
        self.storage_utils.select_collection("tools")

        if config.get('ChromaDB', 'DBFreshStart') == 'True':
            self.storage_utils.reset_memory()
            self.initialize_task_collection()
            self.initialize_tool_collection()

            # tool_data = config.tools()
            # print(tool_data)




