import pinecone

PINECONE_API_KEY = "" #This is where you place your API Key
PINECONE_ENVIRONMENT = "us-east4-gcp" #This is the environment name where your index lives.

YOUR_TABLE_NAME = "test-table"
DIMENSION = 768
METRIC = "cosine"
POD_TYPE = "p1"

def init_pinecone():
    pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

def deinit_pinecone():
    pinecone.deinit()

def create_pinecone_index():
    if YOUR_TABLE_NAME not in pinecone.list_indexes():
        pinecone.create_index(
            YOUR_TABLE_NAME, dimension=DIMENSION, metric=METRIC, pod_type=POD_TYPE
        )

def delete_pinecone_index():
    if YOUR_TABLE_NAME in pinecone.list_indexes():
        pinecone.delete_index(YOUR_TABLE_NAME)

def connect_to_index():
    return pinecone.Index(YOUR_TABLE_NAME)
