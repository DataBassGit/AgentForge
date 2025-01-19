# base_storage.py
from agentforge.config import Config
from agentforge.utils.logger import Logger

class BaseStorage:
    """
    A base class defining the interface that all database adapters should implement.
    Subclasses should override these methods with DB-specific logic.
    """

    # ---------------------------------------------
    # Initialization
    # ---------------------------------------------

    def __init__(self, *args, **kwargs):
        # This might hold a reference to your central config object,
        # or you can instantiate your config here if needed.
        self.config = Config()
        self.logger = Logger("base_storage", 'storage')

        self._init_storage_configs()

    def _init_storage_configs(self):
        self._process_storage_config()
        self._validate_configuration()
        self._load_configuration()

    # ----------------------------------------------
    # Internal Methods - Process Configuration
    # ----------------------------------------------

    def _process_storage_config(self):
        self._get_storage_config()
        self._get_selected_storage()
        self._get_selected_embedding()

    def _get_storage_config(self):
        self.storage_settings = self.config.data['settings']['storage']
        self.storage_options = self.storage_settings['options']
        self.storage_library = self.storage_settings['library']
        self.storage_embedding_library = self.storage_settings['embedding_library']

    def _get_selected_storage(self):
        self.selected_configuration = self.storage_settings['selected_storage'].get('configuration', None)
        self.selected_implementation = self.storage_settings['selected_storage'].get('implementation', None)

    def _get_selected_embedding(self):
        self.selected_embedding = self.storage_settings['embedding'].get('selected', None)

    # ----------------------------------------------
    # Internal Methods - Config Validation
    # ----------------------------------------------

    def _validate_configuration(self):
        self._is_valid_selected_implementation()
        self._is_valid_selected_configuration()
        self._is_valid_selected_embedding()

    def _is_valid_selected_implementation(self):
        if self.selected_implementation not in self.storage_library:
            raise NotImplementedError(f"The selected storage implementation '{self.selected_implementation}' does "
                                      f"not exist in the storage library!")

    def _is_valid_selected_configuration(self):
        if self.selected_configuration not in self.storage_library[self.selected_implementation]['configurations']:
            raise NotImplementedError(f"The selected storage configuration '{self.selected_configuration}' does not "
                                      f"exist not exist in the library configuration '{self.selected_configuration}'!")

    def _is_valid_selected_embedding(self):
        if self.selected_embedding not in self.storage_embedding_library:
            raise NotImplementedError(f"The selected storage embedding '{self.selected_embedding}' does "
                                      f"not exist in the embedding library'!")

    # ----------------------------------------------
    # Internal Methods - Load Selected Configuration
    # ----------------------------------------------

    def _load_configuration(self):
        self._load_storage_implementation()
        self._load_storage_configuration()
        self._load_storage_embedding()
        self._load_storage_path()

    def _load_storage_implementation(self):
        self.storage_implementation = self.storage_library.get(self.selected_implementation)

    def _load_storage_configuration(self):
        self.storage_configuration = self.storage_implementation['configurations'].get(self.selected_configuration)

    def _load_storage_embedding(self):
        self.storage_embedding = self.storage_embedding_library.get(self.selected_embedding)

    def _load_storage_path(self):
        self.storage_path = self.storage_options.get('persist_directory')

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

    def select_or_create_collection(self, collection_name):
        """
        Select or focus on a particular 'collection' or table within the DB.
        Automatically create the given collection or table if it does not already exist.
        Returns an object or handle representing that collection, or modifies state.
        """
        raise NotImplementedError("Subclass must implement 'select_or_create_collection'")

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

