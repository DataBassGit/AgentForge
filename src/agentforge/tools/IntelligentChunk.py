import spacy
# from ..utils.storage_interface import StorageInterface


def intelligent_chunk(text, chunk_size):
    # Define the number of sentences per chunk based on the chunk_size
    sentences_per_chunk = {
        0: 5,
        1: 13,
        2: 34,
        3: 55
    }
    
    # Load the spacy model (you can use a different model if you prefer)
    # nlp = StorageInterface().storage_utils.return_embedding(str(text))
    # Increase the max_length limit to accommodate large texts
    nlp = spacy.blank('en')
    nlp.add_pipe('sentencizer', config={"punct_chars": None})
    nlp.max_length = 3000000
    
    # Tokenize the text into sentences using spacy
    doc = nlp(str(text))
    sentences = [sent.text for sent in doc.sents]
    
    # Determine the number of sentences per chunk based on the input chunk_size
    num_sentences = sentences_per_chunk.get(chunk_size)
    
    # Group the sentences into chunks with a 2-sentence overlap
    chunks = []
    i = 0
    while i < len(sentences):
        chunk = '\n'.join(sentences[i:i + num_sentences])
        chunks.append(chunk)
        i += num_sentences - 2  # Move the index forward by (num_sentences - 2) to create the overlap
    # print(f"Chunks: {chunks}")
    return chunks


# # Example usage
# text = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence."
# chunks = intelligent_chunk(text, chunk_size=0)
# print(chunks)
