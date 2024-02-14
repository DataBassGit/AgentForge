from ..config import Config


class StorageInterface:
    _instance = None
    storage_utils = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            try:
                cls.config = Config()
                cls._instance = super(StorageInterface, cls).__new__(cls, *args, **kwargs)
                cls._instance.initialize_storage()
            except Exception as e:
                print(f"Error initializing StorageInterface: {e}")
                raise
        return cls._instance

    def __init__(self):
        # Add your initialization code here
        pass

    def initialize_chroma(self):
        from .chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()

        if self.config.data['settings']['storage']['ChromaDB']['DBFreshStart'] == 'True':
            self.storage_utils.reset_memory()

    def initialize_pinecone(self):
        try:
            from agentforge.utils.pinecone_utils import PineconeUtils
            self.storage_utils = PineconeUtils()
            self.storage_utils.init_storage()
        except Exception as e:
            print(f"An error occurred: {e}")

    def initialize_storage(self):
        if self.storage_utils is None:
            storage_api = self.config.data['settings']['storage']['StorageAPI']

            if storage_api == 'ChromaDB':
                self.initialize_chroma()
                return
            if storage_api == 'Pinecone':
                self.initialize_pinecone()
                return
            else:
                raise ValueError(f"Unsupported Storage API library: {storage_api}")