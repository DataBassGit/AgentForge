# base_storage.py
from agentforge.config import Config
from agentforge.utils.logger import Logger

class BaseStorage:
    """
    A base class defining the interface that all database adapters should implement.
    Subclasses should override these methods with DB-specific logic.
    """

    # ---------------------------------
    # Initialization
    # ---------------------------------

    def __init__(self, *args, **kwargs):
        # This might hold a reference to your central config object,
        # or you can instantiate your config here if needed.
        self.current_collection = None
        self.storage_path: str = ''
        self.storage_embedding: str =''

        self.config = Config()
        self.logger = Logger("Chroma Utils", 'storage')

        self._load_storage_path_and_embedding()

    # ---------------------------------
    # Internal Methods
    # ---------------------------------

    def _load_storage_path_and_embedding(self):
        """
        Loads (and returns) the relevant storage settings from the config.
        Subclasses can call this to figure out any paths or embedding preferences.
        """
        # This is the universal source of truth for settings.
        storage_settings = self.config.data['settings'].get('storage', {})
        self.storage_path = storage_settings['options'].get('persist_directory', None)
        self.storage_embedding = storage_settings['embedding'].get('selected', None)

    # ---------------------------------
    # Implementation
    # ---------------------------------

    def connect(self):
        """
        Establish a connection to the database.
        Subclasses must override this method with specific connection logic.
        """
        raise NotImplementedError("Subclass must implement 'connect'")

    def disconnect(self):
        """
        Disconnect from the database or release any resources.
        """
        raise NotImplementedError("Subclass must implement 'disconnect'")

    def select_collection(self, collection_name):
        """
        Select or focus on a particular 'collection' or table within the DB.
        Returns an object or handle representing that collection, or modifies state.
        """
        raise NotImplementedError("Subclass must implement 'select_collection'")

    def create_collection(self, collection_name):
        """
        Create a new collection (or table) within the database.
        """
        raise NotImplementedError("Subclass must implement 'create_collection'")

    def delete_collection(self, collection_name):
        """
        Delete a collection (or table) from the database.
        """
        raise NotImplementedError("Subclass must implement 'delete_collection'")

    def set_current_collection(self, collection_name):
        """
        Set the current collection (or table).
        """
        raise NotImplementedError("Subclass must implement 'set_current_collection'")

    def insert(self, collection_name, data):
        """
        Insert a record or list of records into the specified collection.
        """
        raise NotImplementedError("Subclass must implement 'insert'")

    def query(self, collection_name, query):
        """
        Perform a query on the specified collection and return matching results.
        """
        raise NotImplementedError("Subclass must implement 'query'")

    def update(self, collection_name, query, new_data):
        """
        Update records in the collection that match the query, replacing data accordingly.
        """
        raise NotImplementedError("Subclass must implement 'update'")

    def delete(self, collection_name, query):
        """
        Delete records from the collection matching the query.
        """
        raise NotImplementedError("Subclass must implement 'delete'")

    def count(self, collection_name):
        """
        Return the number of documents or rows in the given collection.
        """
        raise NotImplementedError("Subclass must implement 'count'")

    def reset_storage(self):
        """
        Clear or reset all data in the storage.
        Subclasses must override this if they support data resets.
        """
        raise NotImplementedError("Subclass must implement 'reset_storage'")

