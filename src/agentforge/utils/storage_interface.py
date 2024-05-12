from ..config import Config


class StorageInterface:
    """
    A singleton class designed to initialize and provide access to specific storage utilities based on the storage
    settings YAML file.

    This class supports initializing different types of storage APIs like ChromaDB and Pinecone, as specified in the
    application's configuration settings. It ensures that only one instance of each storage utility is created
    throughout the application's lifecycle.

    Attributes:
        _instance (StorageInterface): A private class attribute to hold the singleton instance.
        storage_utils: The initialized storage utility object (e.g., ChromaUtils, PineconeUtils).
    """
    _instance = None
    storage_utils = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of StorageInterface is created (singleton pattern). Initializes the storage
        utility based on the application's configuration settings.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            StorageInterface: The singleton instance of the StorageInterface class.
        """
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
        """
        Placeholder for the initialization code. Actual initialization of the storage utility is handled in the
        __new__ method.
        """
        pass

    def initialize_chroma(self):
        """
        Initializes the ChromaDB storage utility and resets its memory if specified in the configuration settings.
        """
        from .chroma_utils import ChromaUtils
        self.storage_utils = ChromaUtils()

        if self.config.data['settings']['storage']['ChromaDB']['DBFreshStart'] is True:
            self.storage_utils.reset_memory()

    def initialize_pinecone(self):
        """
        Initializes the Pinecone storage utility and calls its initialization method.

        # CURRENTLY NOT WORKING - FIX COMING SOON
        """
        try:
            from agentforge.utils.pinecone_utils import PineconeUtils
            self.storage_utils = PineconeUtils()
            self.storage_utils.init_storage()
        except Exception as e:
            print(f"An error occurred: {e}")

    def initialize_storage(self):
        """
        Determines the storage API to initialize based on the application's configuration settings.

        This method reads the 'StorageAPI' setting from the configuration and calls the appropriate initialization
        method for the specified storage utility.

        Raises:
            ValueError: If the specified StorageAPI is not supported by the application.
        """
        if self.storage_utils is None:
            storage_api = self.config.data['settings']['storage']['StorageAPI']

            if storage_api is None:
                self.storage_utils = None
                return
            if storage_api == 'ChromaDB':
                self.initialize_chroma()
                return
            if storage_api == 'Pinecone':
                self.initialize_pinecone()
                return

            raise ValueError(f"Unsupported Storage API library: {storage_api}")
