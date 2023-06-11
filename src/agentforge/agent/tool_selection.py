from ..utils import storage_interface

storage = storage_interface.StorageInterface()

action = storage.storage_utils.load_collection(
    collection_name='actions',
    limit=1,
)
tools_used = action["metadatas"][0]['tools_used']

tools = storage.storage_utils.query_memory(
    collection_name='tools',
    where={'tools_used': tools_used},
    include=['metadatas'],
)

for tool in tools['metadatas']:
    print(tool)
