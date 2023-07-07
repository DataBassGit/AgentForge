from agentforge.utils.storage_interface import StorageInterface
from scipy.spatial import distance
from sklearn.metrics.pairwise import cosine_distances

storage = StorageInterface().storage_utils

# query = """Sure, I can provide some general steps on how to search for something online:
#
# 1. Open a web browser: This could be any web browser such as Google Chrome, Mozilla Firefox, Safari, or Microsoft Edge.
#
# 2. Use a search engine: Once you have your web browser open, navigate to a search engine. The most popular search engine is Google, but there are others such as Bing, Yahoo, and DuckDuckGo.
#
# 3. Enter your search terms: In the search box of the search engine, type in what you're looking for. This could be a question, keywords related to a topic, a website name, etc.
#
# 4. Review the search results: Once you hit enter or click the search button, you'll be provided with a list of results that the search engine thinks are relevant to your query. These can include websites, images, videos, and more.
#
# 5. Click on a result to view more: When you find a result that looks like it might contain the information you're looking for, click on it to navigate to the page and view more.
#
# In addition to these basic steps, there are also several strategies you can use to find information more effectively. These include:
#
# - Using quotation marks to search for an exact phrase: For example, searching for "chocolate cake recipe" will return pages where those three words appear together in that order.
#
# - Using the word 'site:' followed by a website URL to search within a specific website. For example, if you only wanted to search Wikipedia for information on dinosaurs, you would enter "dinosaurs site:wikipedia.org" in the search bar.
#
# - Using a minus sign to exclude certain words from your search. For example, if you were looking for information about eagles the bird, but not the Eagles the band, you could search for "eagles -band".
#
# Remember, it's important to critically evaluate the information you find online, as not all sources are equally reliable. Look for information from reputable sources and cross-check facts where possible."""

query = "What's the recipe for making a universe?"

# query = "The 'GoogleSearch' tool searches the web for a specified query and retrieves a set number of results. Each result consists of a URL and a short snippet describing its contents."


params = {
    "collection_name": 'tools',
    "query": query,
    "include": ["embeddings", "documents", "metadatas", "distances"]
}

text_search = storage.query_memory(params)
print('')
print('Text Search')
print(text_search)
# print(text_search['documents'])

query_emb = storage.return_embedding(query)

params = {
    "collection_name": 'tools',
    "embeddings": query_emb,
    "include": ["embeddings", "documents", "metadatas", "distances"]
}

emb_search = storage.query_embedding(params)
print('')
print('Embedding Search')
print(emb_search)
# print(emb_search['documents'])

distance = distance.cosine(query_emb[0], text_search['embeddings'][0][0])
print('')
print('Distance')
print(distance)


