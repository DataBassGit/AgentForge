from semantic_router.splitters import RollingWindowSplitter
from semantic_router.encoders import FastEmbedEncoder

# needed modules:
# pip install --user semantic-router
# pip install --user 'semantic-router[fastembed]'


def semantic_chunk(text: str) -> list:
    """
    Split a given text into chunks based on semantic similarity.

    This function takes a string of text and breaks it down into smaller chunks,
    where each chunk represents a semantically similar portion of the text.
    The chunking is performed based on the semantic meaning and coherence of the
    text, rather than a fixed size or specific delimiters.

    Args:
        text (str): The input text to be chunked.

    Returns:
        list: A list of dicts, where each dict represents a semantically
            similar chunk of the input text. You will want the 'content' key of
            each item in the list.

    Example:
        >>> text = "This is a sample text. It consists of multiple sentences. Each sentence conveys a specific idea or thought."
        >>> chunks = semantic_chunk(text)
        >>> for c in chunks:
        >>> print(r.content)
        ['This is a sample text.', 'It consists of multiple sentences.', 'Each sentence conveys a specific idea or thought.']
    """

    encoder = FastEmbedEncoder(name="sentence-transformers/all-MiniLM-L6-v2")
    splitter = RollingWindowSplitter(
        encoder=encoder,
        dynamic_threshold=True,
        min_split_tokens=100,
        max_split_tokens=500,
        window_size=2,
        plot_splits=False,  # set this to true to visualize chunking
        enable_statistics=True  # to print chunking stats
    )

    splits = splitter([text])
    splitter.print(splits)
    return splits


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
