import configparser
import pinecone

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
storage_api_key = config.get('Pinecone', 'api_key')
storage_environment = config.get('Pinecone', 'environment')
table_name = config.get('Pinecone', 'index_name')
dimension = config.get('Pinecone', 'dimension')
metric = "cosine"
pod_type = "p1"

# Global variable for storage index
storage_index = None


def init_storage():
    pinecone.init(storage_api_key, storage_environment)


def destroy_storage():
    pinecone.deinit()


def create_storage():
    if table_name not in pinecone.list_indexes():
        pinecone.create_index(
            table_name, dimension, metric, pod_type
        )
    global storage_index
    storage_index = pinecone.Index(table_name)


def delete_storage_index():
    if table_name in pinecone.list_indexes():
        pinecone.delete_index(table_name)


def connect_to_index():
    return pinecone.Index(table_name)


# Accessor function to get the storage index
def get_storage_index():
    global storage_index
    return storage_index

