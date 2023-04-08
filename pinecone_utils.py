import configparser
import pinecone

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')
STORAGE_API_KEY = config.get('Pinecone', 'api_key')
STORAGE_ENVIRONMENT = config.get('Pinecone', 'environment')


YOUR_TABLE_NAME = "test-table"
DIMENSION = 768
METRIC = "cosine"
POD_TYPE = "p1"


def init_storage():
    pinecone.init(api_key=STORAGE_API_KEY, environment=STORAGE_ENVIRONMENT)


def deinit_storage():
    pinecone.deinit()


def create_storage_index(table_name):
    dimension = 768
    metric = "cosine"
    pod_type = "p1"
    if table_name not in pinecone.list_indexes():
        pinecone.create_index(
            table_name, dimension=dimension, metric=metric, pod_type=pod_type
        )
    global storage_index
    storage_index = pinecone.Index(table_name)


def delete_storage_index(table_name):
    if table_name in pinecone.list_indexes():
        pinecone.delete_index(table_name)


def connect_to_index(table_name):
    return pinecone.Index(table_name)
