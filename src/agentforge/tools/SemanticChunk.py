from semantic_chunkers import StatisticalChunker
from semantic_router.encoders import FastEmbedEncoder

class Chunk:
    def __init__(self, is_triggered, triggered_score, token_count, splits):
        self.is_triggered = is_triggered
        self.triggered_score = triggered_score
        self.token_count = token_count
        self.splits = splits
        self.content = ' '.join(splits)  # Join splits for content

def semantic_chunk(text: str) -> list[Chunk]:
    """
    Perform semantic chunking on the input text.

    This function uses a StatisticalChunker with a FastEmbedEncoder to split the input text
    into semantically coherent chunks. It's designed to handle large texts by breaking them
    down into smaller, meaningful segments.

    Args:
        text (str): The input text to be chunked.

    Returns:
        list[Chunk]: A list of Chunk objects, each representing a semantic chunk of the input text.
        Each Chunk object has the following attributes:
            - is_triggered (bool): Indicates if the chunk was triggered by the chunking algorithm.
            - triggered_score (float): The score that triggered the chunk split.
            - token_count (int): The number of tokens in the chunk.
            - splits (list[str]): The individual text segments that make up the chunk.
            - content (str): The full text content of the chunk (joined splits).

    Note:
        This function uses the 'sentence-transformers/all-MiniLM-L6-v2' model for encoding.
        The chunker is configured with specific parameters for token limits and window size,
        which can be adjusted if needed.
    """
    encoder = FastEmbedEncoder(name="sentence-transformers/all-MiniLM-L6-v2")
    chunker = StatisticalChunker(
        encoder=encoder,
        dynamic_threshold=True,
        min_split_tokens=128,
        max_split_tokens=1024,
        window_size=2,
        enable_statistics=True  # to print chunking stats
    )

    chunks = chunker([text])
    chunker.print(chunks[0])

    result = []
    for chunk in chunks[0]:
        chunk_obj = Chunk(
            is_triggered=chunk.is_triggered,
            triggered_score=chunk.triggered_score,
            token_count=chunk.token_count,
            splits=chunk.splits
        )
        result.append(chunk_obj)

    return result



if __name__ == '__main__':
    import io
    import requests
    from PyPDF2 import PdfReader

    url = 'https://arxiv.org/pdf/2404.16811.pdf'
    response = requests.get(url)

    if response.status_code == 200:
        pdf_content = io.BytesIO(response.content)
        pdf_reader = PdfReader(pdf_content)
        text2 = ""
        for page in pdf_reader.pages:
            text2 += page.extract_text()
        results = semantic_chunk(text2)
        for r in results:
            print(r.content)
    else:
        print(f"Failed to download the PDF. Status code: {response.status_code}")