import requests
import re

from bs4 import BeautifulSoup
from ..tools.IntelligentChunk import intelligent_chunk
from ..utils.chroma_utils import ChromaUtils as storage

storage_instance = storage()  # Create an instance of ChromaUtils


def remove_extra_newlines(chunk):
    return re.sub(r'\n+', '\n\n', chunk)


def get_plain_text(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Create a BeautifulSoup object with the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the plain text from the HTML content
    plain_text = soup.get_text()
    chunk_text = intelligent_chunk(plain_text, chunk_size=1)
    chunk_save(chunk_text, url)

    return f"Webpage saved to memory!\nURL: {url}"


def chunk_save(chunks, url):
    for chunk in chunks:
        chunk = remove_extra_newlines(chunk)
        params = {
            'data': [chunk],
            'collection_name': 'Results',
            'metadata': [{"source_url": url}]
        }
        storage_instance.save_memory(params)