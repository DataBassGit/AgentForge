from sentence_transformers import SentenceTransformer

# Load the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/LaBSE')

def get_ada_embedding(text: str):
    # Get the embedding for the given text
    embedding = model.encode([text])
    return embedding[0]
