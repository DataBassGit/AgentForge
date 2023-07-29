import uuid
from .. import config


def metadata_builder(collection_name, name, details):
    if collection_name == 'Tasks':
        metadata = {
            "Status": "not completed",
            "Description": details,
            "List_ID": str(uuid.uuid4()),
            "Order": name + 1
        }

    if collection_name == 'Tools':
        metadata = {
            'Name': name,
            'Args': details['Instruction'],
            'Command': details['Command'],
            'Description': details['Description'],
            'Example': details['Example'],
            'Instruction': details['Instruction']
        }

    if collection_name == 'Actions':
        metadata = {
            'Name': name,
            'Description': details['Description'],
            'Example': details['Example'],
            'Instruction': details['Instruction'],
            'Tools': ', '.join(details['Tools'])
        }

    return metadata


def description_extractor(metadata):
    return metadata["Description"]


def id_generator(data):
    return [str(i + 1) for i in range(len(data))]


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

    def initialize_memory(self, memory, extra):
        """
        Initializes a collection with provided data source and metadata builder.
        """

        data = config.data(memory)()
        collection_name = memory
        builder = metadata_builder
        generator = id_generator
        extractor = description_extractor

        if data == 'Invalid case':
            return

        ids = generator(data)

        if isinstance(data, list):
            metadatas = [builder(collection_name, i, item) for i, item in enumerate(data)]
        else:
            metadatas = [builder(collection_name, key, value) for key, value in data.items()]

        description = [extractor(metadata) for metadata in metadatas]

        save_params = {
            "collection_name": collection_name,
            "ids": ids,
            "data": description,
            "metadata": metadatas,
        }

        self.storage_utils.select_collection(collection_name)
        self.storage_utils.save_memory(save_params)

    def initialize_chroma(self):
        from .chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()
        self.storage_utils.init_storage()

        if config.get('ChromaDB', 'DBFreshStart') == 'True':
            self.storage_utils.reset_memory()
            memories = config.persona()['Memories']

            [self.initialize_memory(key, value) for key, value in memories.items()]


