import configparser
import chromadb
from chromadb.config import Settings

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
CHROMA_DB_IMPL = config.get('ChromaDB', 'chroma_db_impl')
PERSIST_DIRECTORY = config.get('ChromaDB', 'persist_directory', fallback=None)
YOUR_COLLECTION_NAME = config.get('ChromaDB', 'collection_name')

global client
global collection


def init_storage():
    global client
    settings = Settings(CHROMA_DB_IMPL)
    if PERSIST_DIRECTORY:
        settings.persist_directory = PERSIST_DIRECTORY
    client = chromadb.Client(settings)


def deinit_storage():
    global client
    client = None


def create_collection(collection_name):
    # global client
    if collection_name not in client.list_collections():
        client.create_collection(collection_name)
    global collection
    collection = client.get_collection(collection_name)

    # print(collection)


def delete_collection(collection_name):
    if collection_name in client.list_collections():
        client.delete_collection(collection_name)