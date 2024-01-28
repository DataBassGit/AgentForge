from agentforge.agents.LearnKGAgent import LearnKGAgent
from agentforge.tools.GetText import GetText
from agentforge.tools.IntelligentChunk import intelligent_chunk
from agentforge.tools.InjectKG import Consume
from ..logs.logger_config import Logger

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
    def __init__(self, log_level="info"):
        self.intelligent_chunk = intelligent_chunk
        self.get_text = GetText()
        self.learn_kg = LearnKGAgent()
        self.consumer = Consume()

        self.logger = Logger(name=self.__class__.__name__)
        self.logger.set_level(log_level)

    def process_file(self, file):
        try:
            # Step 1: Extract text from the file
            file_content = self.get_text.read_file(file)
        except Exception as e:
            self.logger.log(f"Error reading file: {e}", 'error')
            return

        try:
            # Step 2: Create chunks of the text
            chunks = self.intelligent_chunk(file_content, chunk_size=2)
        except Exception as e:
            self.logger.log(f"Error chunking text: {e}", 'error')
            return

        for chunk in chunks:
            try:
                # Steps within the loop for learning and injecting data
                data = self.learn_kg.run(chunk=chunk, kg="No Entries")

                if data is not None and 'sentences' in data and data['sentences']:
                    for key in data['sentences']:
                        sentence = data['sentences'][key]
                        reason = data['reasons'].get(key, "")

                        injected = self.consumer.consume(sentence, reason, "Test", file)
                        print(f"The following entry was added to the knowledge graph:\n{injected}\n\n")
                else:
                    self.logger.log("No relevant knowledge was found", 'info')
            except Exception as e:
                self.logger.log(f"Error processing chunk: {e}", 'error')
                continue  # Optionally continue to the next chunk
