from semantic_text_splitter import TextSplitter


class Chunk:
    """
    Represents a chunk of text.

    Attributes:
        content (str): The content of the chunk.
    """

    def __init__(self, content):
        """
        Initialize a Chunk object.

        Args:
            content (str): The content of the chunk.
        """
        self.content = content


def semantic_chunk(text, min_length=200, max_length=2000):
    """
    Split text into semantic chunks using the semantic_text_splitter library.

    This function splits the input text into chunks based on semantic meaning,
    with each chunk having a length between min_length and max_length.

    Args:
        text (str): The input text to be chunked.
        min_length (int, optional): The minimum length of each chunk. Defaults to 200.
        max_length (int, optional): The maximum length of each chunk. Defaults to 2000.

    Returns:
        list: A list of Chunk objects, each containing a portion of the input text.

    Raises:
        ValueError: If the input text is not a string, or if min_length or max_length are invalid.
        ImportError: If the semantic_text_splitter library is not installed.
        Exception: For any other unexpected errors during execution.
    """
    if not isinstance(text, str):
        raise ValueError("Input text must be a string")
    
    if not isinstance(min_length, int) or not isinstance(max_length, int):
        raise ValueError("min_length and max_length must be integers")
    
    if min_length <= 0 or max_length <= 0 or min_length >= max_length:
        raise ValueError("Invalid min_length or max_length values")

    try:
        splitter = TextSplitter((min_length, max_length), trim=False)

        chunks = splitter.chunks(text)
        result = []
        for chunk in chunks:
            # Preserve intentional line breaks while removing extra whitespace
            cleaned_chunk = '\n'.join(' '.join(line.split()) for line in chunk.split('\n'))
            chunk_obj = Chunk(content=cleaned_chunk)
            result.append(chunk_obj)

        return result

    except ImportError:
        raise ImportError("semantic_text_splitter library is not installed. Please install it to use this function.")
    except Exception as e:
        raise Exception(f"An error occurred while chunking the text: {str(e)}")

# Usage example (commented out)
# if __name__ == "__main__":
#     try:
#         text = "This is a sample text. It contains multiple sentences. " * 20
#         chunks = semantic_chunk(text)
#         print(f"Number of chunks: {len(chunks)}")
#         for i, chunk in enumerate(chunks, 1):
#             print(f"Chunk {i}: {chunk.content[:50]}...")  # Print first 50 characters of each chunk
#     except Exception as e:
#         print(f"Error: {str(e)}")

