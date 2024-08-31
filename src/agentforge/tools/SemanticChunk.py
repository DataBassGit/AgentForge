from semantic_text_splitter import TextSplitter


class Chunk:
    def __init__(self, content):
        self.content = content


def semantic_chunk(text):

    splitter = TextSplitter((200, 2000), trim=False)

    chunks = splitter.chunks(text)
    result = []
    for chunk in chunks:
        chunk_obj = Chunk(content=chunk)
        result.append(chunk_obj)

    return result

