from agentforge.agents.LearnKGAgent import LearnKGAgent
from agentforge.tools.GetText import GetText
from agentforge.tools.IntelligentChunk import intelligent_chunk
# from agentforge.tools.TripleExtract import TripleExtract
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
        self.intelligent_chunk = intelligent_chunk
        self.get_text = GetText()
        self.learn_kg = LearnKGAgent()
        self.consumer = Consume()

    def process_file(self, file):
        # Step 1: Extract text from the file
        file_content = self.get_text.read_file(file)

        # Step 2: Create chunks of the text
        chunks = self.intelligent_chunk(file_content, chunk_size=2)

        # Step 3: Process each chunk
        for chunk in chunks:

            # Learn from the triples
            data = self.learn_kg.run(chunk=chunk, kg="No Entries")
            # sentences returns as a yaml object.

            # Inject into the database
            if data is not None and 'sentences' in data and data['sentences']:
                for key in data['sentences']:
                    sentence = data['sentences'][key]
                    reason = data['reasons'].get(key, "")  # Get the corresponding reason, or empty if not found

                    # Assuming you have a consumer object with a consume method
                    injected = self.consumer.consume(sentence, reason, "Test", file)
                    print(f"The following entry was added to the knowledge graph:\n{injected}\n\n")
            else:
                print("No relevant knowledge was found")
