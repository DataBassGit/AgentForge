import spacy


def intelligent_chunk(text, chunk_size):
    """
    Intelligently chunk a given text into smaller segments based on sentence structure.

    This function uses spaCy to tokenize the text into sentences and then groups these
    sentences into chunks of a specified size, with a 2-sentence overlap between chunks.

    Args:
        text (str): The input text to be chunked.
        chunk_size (int): An integer (0-3) representing the desired chunk size.
            0: Very small (5 sentences)
            1: Small (13 sentences)
            2: Medium (34 sentences)
            3: Large (55 sentences)

    Returns:
        list: A list of text chunks, where each chunk is a string.

    Raises:
        ValueError: If the chunk_size is not in the range 0-3, or if the input text is not a string.
        ImportError: If spaCy is not installed or the English model is not available.
        Exception: For any other unexpected errors during execution.
    """
    # Define the number of sentences per chunk based on the chunk_size
    sentences_per_chunk = {
        0: 5,
        1: 13,
        2: 34,
        3: 55
    }
    
    if not isinstance(text, str):
        raise ValueError("Input text must be a string")
    
    if chunk_size not in sentences_per_chunk:
        raise ValueError("chunk_size must be an integer between 0 and 3")

    try:
        # Load the spacy model
        nlp = spacy.blank('en')
        nlp.add_pipe('sentencizer', config={"punct_chars": None})
        nlp.max_length = 3000000  # Increase the max_length limit to accommodate large texts
        
        # Tokenize the text into sentences using spacy
        doc = nlp(str(text))
        sentences = [sent.text for sent in doc.sents]
        
        # Determine the number of sentences per chunk based on the input chunk_size
        num_sentences = sentences_per_chunk[chunk_size]
        
        # Group the sentences into chunks with a 2-sentence overlap
        chunks = []
        i = 0
        while i < len(sentences):
            chunk = '\n'.join(sentences[i:i + num_sentences])
            chunks.append(chunk)
            i += num_sentences - 2  # Move the index forward by (num_sentences - 2) to create the overlap
        
        return chunks

    except ImportError:
        raise ImportError("spaCy is not installed or the English model is not available. Please install spaCy and download the English model.")
    except Exception as e:
        raise Exception(f"An error occurred while chunking the text: {str(e)}")

# # Example usage
# text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence."
# chunks = intelligent_chunk(text, chunk_size=0)
# print(chunks)
