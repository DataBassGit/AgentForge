import uuid


from .. import config

# def metadata_builder(name, details):
#
#     if name == 'tasks':
#         metadata = {
#             "task_status": "not completed",
#             "task_desc": details,
#             "list_id": str(uuid.uuid4()),
#             "task_order": name + 1
#         }
#
#     if name == 'tools':
#         metadata = {
#             'Name': name,
#             'Description': details['Description'],
#             'Example': details['Example'],
#             'Instruction': details['Instruction']
#         }
#
#
#         {
#             'Name': name,
#             'Description': details['Description'],
#             'Example': details['Example'],
#             'Instruction': details['Instruction'],
#             'Tools': ', '.join(details['Tools'])
#         }
#
#     return metadata

def tools_metadata_builder(name, details):
    return {
        'Name': name,
        'Description': details['Description'],
        'Example': details['Example'],
        'Instruction': details['Instruction']
    }


def tools_id_generator(data):
    return [str(i + 1) for i in range(len(data))]


def tools_description_extractor(metadata):
    return metadata['Description']


def task_metadata_builder(name, details):
    return {
        "task_status": "not completed",
        "task_desc": details,
        "list_id": str(uuid.uuid4()),
        "task_order": name + 1
    }


def task_id_generator(data):
    return [str(i + 1) for i in range(len(data))]


def task_description_extractor(metadata):
    return metadata["task_desc"]


# def metadata_extractor(metadata, extract):
#     return metadata[extract]
#
#
# def id_generator(data):
#     return [str(i + 1) for i in range(len(data))]

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

    def initialize_action_collection(self):
        """
        Initializes the tools collection with the data from tools.json.
        """
        action_data = config.actions()

        metadatas = [{
            'Name': name,
            'Description': details['Description'],
            'Example': details['Example'],
            'Instruction': details['Instruction'],
            'Tools': ', '.join(details['Tools'])
        } for name, details in action_data.items()]

        ids = [str(i + 1) for i in range(len(action_data))]
        description = [metadata['Description'] for metadata in metadatas]
        # action_names = [metadata['Name'] for metadata in metadatas]

        params = {
            "collection_name": 'actions',
            "ids": ids,
            "data": description,
            "metadata": metadatas,
        }

        self.storage_utils.save_memory(params)

    def initialize_memory(self, params):
        """
        Initializes a collection with provided data source and metadata builder.
        """
        data_source = params['data_source']
        collection_name = params['collection_name']
        metadata_builder = params['metadata_builder']
        id_generator = params['id_generator']
        description_extractor = params['description_extractor']
        list_key = params.get('list_key', None)

        data_dict = data_source()
        data = data_dict[list_key] if list_key else data_dict

        ids = id_generator(data)

        if isinstance(data, list):
            metadatas = [metadata_builder(i, item) for i, item in enumerate(data)]
        else:
            metadatas = [metadata_builder(key, value) for key, value in data.items()]

        description = [description_extractor(metadata) for metadata in metadatas]

        save_params = {
            "collection_name": collection_name,
            "ids": ids,
            "data": description,
            "metadata": metadatas,
        }

        self.storage_utils.save_memory(save_params)

    # def create_memory_collection(self, memory, data):
    #
    #     data = config.switch_case(data)
    #
    #     params = {
    #         # 'data_source': config.persona,
    #         # 'collection_name': 'tasks',
    #         'data_source': data,
    #         'collection_name': memory,
    #         'metadata_builder': task_metadata_builder,
    #         'id_generator': id_generator,
    #         'description_extractor': metadata_extractor,
    #         # 'list_key': 'Tasks'  # Optional | specify the key in the dictionary that contains the list
    #     }
    #
    #     self.storageInt.initialize_memory(params)

    def initialize_chroma(self):
        from .chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()
        self.storage_utils.init_storage()
        self.storage_utils.select_collection("tasks")
        self.storage_utils.select_collection("results")

        # self.storage_utils.select_collection("actions")
        # self.storage_utils.select_collection("tools")

        if config.get('ChromaDB', 'DBFreshStart') == 'True':
            self.storage_utils.reset_memory()
            # self.initialize_task_collection()
            # self.initialize_action_collection()
            # self.initialize_tool_collection()
            memories = config.persona()['Memories']

            # [self.initialize_memory(key, value) for key, value in memories.items()]

            params = {
                # 'data_source': config.persona,
                'data_source': config.switch_case('Persona'),
                'collection_name': 'tasks',
                'metadata_builder': task_metadata_builder,
                'id_generator': task_id_generator,
                'description_extractor': task_description_extractor,
                'list_key': 'Tasks'  # specify the key in the dictionary that contains the list
            }

            self.initialize_memory(params)

            # params = {
            #     'data_source': config.tools,
            #     'collection_name': 'tools',
            #     'metadata_builder': tools_metadata_builder,
            #     'id_generator': tools_id_generator,
            #     'description_extractor': tools_description_extractor
            # }
            #
            # memory = self.initialize_memory(params)




