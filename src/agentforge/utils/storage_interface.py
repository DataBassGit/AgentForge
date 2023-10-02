import uuid
from ..config import Config


def metadata_builder(collection_name, order, details):
    if collection_name == 'Tasks':
        return {
            "Status": "not completed",
            "Description": details.strip(),
            "List_ID": str(uuid.uuid4()),
            "Order": order + 1  # assuming Name is passed in details for Tasks
        }
    else:
        return details


def metadata_list_builder(order, details):
    return {
        "Description": details.strip(),
        "Order": order  # assuming Name is passed in details for Tasks
    }


def description_extractor(metadata):
    return metadata["Description"]


def id_generator(data):
    return [str(i + 1) for i in range(len(data))]


class StorageInterface:
    _instance = None
    storage_utils = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls.config = Config()
            cls._instance = super(StorageInterface, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialize_storage()
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        pass

    def initialize_chroma(self):
        from .chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()
        self.storage_utils.init_storage()

        # if self.config.get_info('ChromaDB', 'DBFreshStart') == 'True':
        if self.config.settings['storage']['ChromaDB']['DBFreshStart'] == 'True':
            self.storage_utils.reset_memory()
            storage = self.config.settings['memories']

            [self.prefill_storage(key, value) for key, value in storage.items()]

    def initialize_storage(self):
        if self.storage_utils is None:
            # storage_api = self.config.get_storage_api()
            storage_api = self.config.settings['storage']['StorageAPI']

            if storage_api == 'ChromaDB':
                self.initialize_chroma()
                return
            if storage_api == 'rabbitmq':
                # self.initialize_rabbitmq()
                return
            if storage_api == 'Pinecone':
                # self.initialize_pinecone()
                return
            else:
                raise ValueError(f"Unsupported Storage API library: {storage_api}")

    def prefill_storage(self, storage, data):
        """Initializes a collection with provided data source and metadata builder."""

        if not data:
            data = self.config.get_config_element(storage)

            if data == 'Invalid case':
                return

        collection_name = storage
        builder = metadata_builder
        extractor = description_extractor
        generator = id_generator
        ids = generator(data)

        # metadata = None
        #
        # if isinstance(data, list):
        #     description = [item for item in data]

        # metadata = [builder(collection_name, key, value) for key, value in data.items()]

        if isinstance(data, list):
            metadata = [builder(collection_name, i, item) for i, item in enumerate(data)]
        else:
            metadata = [builder(collection_name, key, value) for key, value in data.items()]

        description = [extractor(meta) for meta in metadata]

        save_params = {
            "collection_name": collection_name,
            "ids": ids,
            "data": description,
            "metadata": metadata,
        }

        self.storage_utils.select_collection(collection_name)
        self.storage_utils.save_memory(save_params)

    # def initialize_rabbitmq(self):
    #     try:
    #         from agentforge.utils.amqp_utils import AMQPUtils
    #         self.storage_utils = AMQPUtils()
    #         self.storage_utils.init_storage()
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

    def initialize_pinecone(self):
        try:
            from agentforge.utils.pinecone_utils import PineconeUtils
            self.storage_utils = PineconeUtils()
            self.storage_utils.init_storage()
        except Exception as e:
            print(f"An error occurred: {e}")
