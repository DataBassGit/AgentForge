from agentforge.agents.LearnKG import LearnKG
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface
from agentforge.tools.GetText import GetText
from agentforge.tools.IntelligentChunk import intelligent_chunk

'''
This needs to receive a file path and send that as an argument to GetText.
GetText will return the contents of the file.
The contents will be fed to IntelligentChunk.
Chunks are then fed to LearnKG.
LearnKG returns sentences.
Sentences are fed to TripleExtract.
TripleExtract returns tuples.
This will inject everything into the database.
'''

class FileProcessor:
    def __init__(self):
        self.get_text = GetText()
        self.intelligent_chunk = intelligent_chunk
        self.triple_extract = TripleExtract()
        self.learn_kg = LearnKG()
        self.storage = StorageInterface().storage_utils

    def process_file(self, filename_or_url):
        # Step 1: Extract text from the file
        file_content = self.get_text.read_file(filename_or_url)

        # Step 2: Create chunks of the text
        chunks = self.intelligent_chunk(file_content, chunk_size=0)

        # Step 3: Process each chunk
        for chunk in chunks:
            # Extract triples from the chunk
            triples = self.triple_extract.find_subject_predicate_object(chunk)

            # Learn from the triples
            sentences = self.learn_kg.learn(triples)

            # Inject into the database
            for sentence in sentences:
                subject, predicate, object_ = self.triple_extract.find_subject_predicate_object(sentence)
                document_uuid = uuid.uuid4()
                params = {
                    "collection_name": "knowledgegraph",
                    "data": [sentence],
                    "ids": [str(document_uuid)],
                    "metadata": [{
                        "id": str(document_uuid),
                        "subject": subject,
                        "predicate": predicate,
                        "object": object_,
                        # Add other metadata as needed
                    }]
                }
                self.storage.save_memory(params)

if __name__ == "__main__":
    filename_or_url = 'path_or_url_to_file'  # Replace with the actual file path or URL
    processor = FileProcessor()
    processor.process_file(filename_or_url)