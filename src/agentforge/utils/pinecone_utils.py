import configparser
import pinecone

# Read the configuration file
config = configparser.ConfigParser()
config.read('Configs/config.ini')
storage_api_key = config.get('Pinecone', 'api_key')
storage_environment = config.get('Pinecone', 'environment')
table_name = config.get('Pinecone', 'index_name')
dimension = config.get('Pinecone', 'dimension')
metric = "cosine"
pod_type = "p1"

# Global variable for storage index
storage_index = None


class PineconeUtils:

    @staticmethod
    def init_storage():
        pinecone.init(storage_api_key, storage_environment)

    @staticmethod
    def destroy_storage():
        pinecone.deinit()

    @staticmethod
    def create_storage():
        if table_name not in pinecone.list_indexes():
            pinecone.create_index(
                table_name, dimension, metric, pod_type
            )
        global storage_index
        storage_index = pinecone.Index(table_name)

    @staticmethod
    def delete_storage_index():
        if table_name in pinecone.list_indexes():
            pinecone.delete_index(table_name)

    @staticmethod
    def connect_to_index(self):
        return pinecone.Index(table_name)

    # Accessor function to get the storage index
    @staticmethod
    def get_storage_index(self):
        global storage_index
        return storage_index

