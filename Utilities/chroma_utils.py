import configparser
import chromadb
from chromadb.config import Settings

global client
global collection

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')

db_path = config.get('ChromaDB', 'persist_directory', fallback=None)
collection_name = config.get('ChromaDB', 'collection_name')
chroma_db_impl = config.get('ChromaDB', 'chroma_db_impl')


def init_storage():
    global client
    settings = Settings(chroma_db_impl)
    if db_path:
        settings.persist_directory = db_path
    client = chromadb.Client(settings)


def unload_storage():
    global client
    client = None


def create_storage():
    if collection_name not in client.list_collections():
        client.create_collection(collection_name)
    global collection
    collection = client.get_collection(collection_name)


def delete_collection():
    if collection_name in client.list_collections():
        client.delete_collection()


def get_collection():
    global collection
    return collection


def save_to_collection(result_id, task, result):
    global collection

    collection.add(
        ids=[result_id],
        metadatas=[task],
        documents=[result]
    )
