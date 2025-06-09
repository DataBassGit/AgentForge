import requests
import re

from bs4 import BeautifulSoup
from agentforge.storage.chroma_storage import ChromaStorage

storage_instance = ChromaStorage.get_or_create(storage_id="web_scrape_tool")  # Use registry-safe pattern


def remove_extra_newlines(chunk):
    """
    Remove extra newlines from a chunk of text.

    Args:
        chunk (str): The input text chunk.

    Returns:
        str: The text chunk with extra newlines removed.

    Raises:
        ValueError: If the input is not a string.
    """
    if not isinstance(chunk, str):
        raise ValueError("Input chunk must be a string")
    return re.sub(r'\n+', '\n\n', chunk)


def get_plain_text(url):
    """
    Fetch and extract plain text from a webpage.

    This function sends a GET request to the specified URL, extracts the plain text
    from the HTML content, chunks the text, and saves the chunks to memory.

    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        str: Plain text retrieved from the URL.

    Raises:
        ValueError: If the URL is not a string or is empty.
        requests.RequestException: If there's an error fetching the webpage.
        Exception: For any other unexpected errors during execution.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string")

    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Create a BeautifulSoup object with the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the plain text from the HTML content
        plain_text = soup.get_text()
        # chunk_text = intelligent_chunk(plain_text, chunk_size=1)
        # chunk_save(chunk_text, url)

        return plain_text

    except requests.RequestException as e:
        raise Exception(f"Error fetching the webpage: {str(e)}")
    except Exception as e:
        raise Exception(f"An error occurred while processing the webpage: {str(e)}")


def chunk_save(chunks, url):
    """
    Save chunks of text to memory.

    This function processes each chunk of text, removes extra newlines,
    and saves it to memory using the ChromaUtils instance.

    Args:
        chunks (list): A list of text chunks to save.
        url (str): The URL associated with the chunks.

    Raises:
        ValueError: If chunks is not a list or url is not a string.
        Exception: For any unexpected errors during saving.
    """
    if not isinstance(chunks, list):
        raise ValueError("Chunks must be a list")
    if not isinstance(url, str):
        raise ValueError("URL must be a string")

    try:
        for chunk in chunks:
            chunk = remove_extra_newlines(chunk)
            storage_instance.save_memory(collection_name='Results', data=[chunk], metadata=[{"source_url": url}])
    except Exception as e:
        raise Exception(f"Error saving chunks to memory: {str(e)}")

# Usage example (commented out)
# if __name__ == "__main__":
#     try:
#         url = "https://example.com"
#         result = get_plain_text(url)
#         print(result)
#     except Exception as e:
#         print(f"Error: {str(e)}")
