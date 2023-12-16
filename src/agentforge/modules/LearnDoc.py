from agentforge.agents.LearnKGAgent import LearnKGAgent
from agentforge.utils.storage_interface import StorageInterface
from agentforge.tools.GetText import GetText
from agentforge.tools.IntelligentChunk import intelligent_chunk
from agentforge.tools.TripleExtract import TripleExtract
from agentforge.tools.InjectKG import Consume

'''
This needs to receive a file path and send that as an argument to GetText.
GetText will return the contents of the file.
The contents will be fed to IntelligentChunk.
Chunks are then fed to LearnKG.
LearnKG returns sentences.
Sentences are fed to TripleExtract.
TripleExtract returns tuples.
This will inject everything into the database using InjectKG.Consume.
'''

class FileProcessor:
    def __init__(self):
        self.get_text = GetText()
        self.intelligent_chunk = intelligent_chunk
        self.triple_extract = TripleExtract()
        self.learn_kg = LearnKGAgent()
        self.storage = StorageInterface().storage_utils
        self.consume = Consume.consume()

    def process_file(self, filename_or_url):
        # Step 1: Extract text from the file
        file_content = self.get_text.read_file(filename_or_url)

        # Step 2: Create chunks of the text
        chunks = self.intelligent_chunk(file_content, chunk_size=0)

        # Step 3: Process each chunk
        for chunk in chunks:

            # Learn from the triples
            sentences = self.learn_kg.run(chunk=chunk)
            # sentences returns as a yaml object.

            # Inject into the database
            for sentence in sentences:
                injected = self.consume(sentence, reason, filename_or_url, filename_or_url)
                print(f"The following entry was added to the knowledge graph:\n{injected}")


if __name__ == "__main__":
    filename_or_url = 'path_or_url_to_file'  # Replace with the actual file path or URL
    processor = FileProcessor()
    processor.process_file(filename_or_url)