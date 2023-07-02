from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .storage_interface import StorageInterface

class SemanticComparator:
    def __init__(self):
        self.collection = StorageInterface().storage_utils.get_collection('tools')
        # self.vectorizer = TfidfVectorizer()

    def compare(self, query):
        # get all documents from the collection
        items = self.collection.get()
        documents = [item["document"] for item in items]

        # transform documents into vector space
        self.vector_space = self.vectorizer.fit_transform(documents)

        # transform query into the same vector space
        query_vector = self.vectorizer.transform([query])

        # compute the cosine similarity with all documents
        similarities = cosine_similarity(self.vector_space, query_vector)

        # return the similarities
        return similarities

    def query(self, query):
        result = self.collection.query(
            query_texts=[query],
            n_results=1,
        )
        return result

# iLoad tools database! [storage interface]
# from json file [tools folder]
# vectors will already be made after loading into db [storage interface]
# vectorize query using same transformer as storage interface [.query function?]
# pull 'embedding' var from db utils [chroma_utils.return_embedding()]
# query db with vectors
# return vectors of matches [include embeddings]
# cosine similarity comparison of results [above]
# select top if above threshold [above]

# Initialize the comparator with the 'tools' collection
# comparator = SemanticComparator('tools')

# Now we can compare a query to the documents
# search = "The 'Intelligent Chunk' tool splits"
# similarities = comparator.compare(search)
#
# print(similarities)

# If you want to get the most similar document
# most_similar_doc_index = similarities.argmax()
# most_similar_doc = tools_docs[most_similar_doc_index]
