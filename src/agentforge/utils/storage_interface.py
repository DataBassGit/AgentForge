from typing import Optional, Dict
from ..config import Config


class StorageInterface:
    """
    A singleton class designed to initialize and provide access to specific storage utilities based on the storage
    settings YAML file.

    This class supports initializing different types of storage APIs like ChromaDB and Pinecone, as specified in the
    application's configuration settings. It ensures that only one instance of each storage utility is created
    throughout the application's lifecycle.
    """
    _instance: Optional['StorageInterface'] = None
    storage_utils: Dict[str, object] = {}

    def __new__(cls, *args, **kwargs) -> 'StorageInterface':
        """
        Ensures that only one instance of StorageInterface is created (singleton pattern).

        Returns:
            StorageInterface: The singleton instance of the StorageInterface class.
        """
        if cls._instance is None:
            cls._instance = super(StorageInterface, cls).__new__(cls)
            cls._instance.config = Config()  # Instance attribute
        return cls._instance

    def __init__(self):
        """
        Placeholder for the initialization code. Actual initialization of the storage utility is handled in the
        __new__ method.
        """
        pass

    def get_storage(self, persona_name: str = 'default') -> Optional[object]:
        """
        Retrieves the storage utility for the specified persona.

        Parameters:
            persona_name (str): The persona name for which to get the storage utility.

        Returns:
            Optional[object]: The initialized storage utility or None if initialization failed.
        """
        if persona_name not in self.storage_utils:
            self.initialize_storage(persona_name)
        return self.storage_utils.get(persona_name)

    def initialize_storage(self, persona_name: str = 'default') -> None:
        """
        Determines the storage API to initialize based on the application's configuration settings.

        Parameters:
            persona_name (str): The persona name for which to initialize the storage utility.

        Raises:
            ValueError: If the specified StorageAPI is not supported by the application.
        """
        storage_enabled = self.config.data['settings']['system'].get('StorageEnabled', False)

        if not storage_enabled:
            self.storage_utils[persona_name] = None
            return

        try:
            storage_api = self.config.data['settings']['storage'].get('StorageAPI')
            if storage_api == 'ChromaDB':
                self.initialize_chroma(persona_name)
            elif storage_api == 'Pinecone':
                self.initialize_pinecone(persona_name)
            else:
                raise ValueError(f"Unsupported Storage API library: {storage_api}")
        except ImportError as e:
            print(f"An import error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def initialize_chroma(self, persona_name: str = 'default') -> None:
        """
        Initializes the ChromaDB storage utility and resets its memory if specified in the configuration settings.

        Parameters:
            persona_name (str): The persona name for which to initialize the storage utility.
        """
        from .chroma_utils import ChromaUtils
        self.storage_utils[persona_name] = ChromaUtils(persona_name)

    def initialize_pinecone(self, persona_name: str = 'default') -> None:
        """
        # CURRENTLY NOT WORKING - IMPLEMENTATION COMING SOON-ISH

        Initializes the Pinecone storage utility and calls its initialization method.

        Parameters:
            persona_name (str): The persona name for which to initialize the storage utility.
        """
        from agentforge.utils.pinecone_utils import PineconeUtils
        self.storage_utils[persona_name] = PineconeUtils()
