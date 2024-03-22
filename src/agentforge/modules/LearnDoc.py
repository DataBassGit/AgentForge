from agentforge.agents.LearnKGAgent import LearnKGAgent
from agentforge.tools.GetText import GetText
from agentforge.tools.IntelligentChunk import intelligent_chunk
from agentforge.modules.InjectKG import Consume
from agentforge.utils.functions.Logger import Logger
from agentforge.tools.CleanString import Strip
from agentforge.utils.storage_interface import StorageInterface
import os


class FileProcessor:
    """
    Processes files to extract text, chunk it intelligently, learn from it using a knowledge graph agent,
    and inject the learned knowledge into a database.

    The class orchestrates a pipeline involving reading text from files, dividing the text into manageable chunks,
    processing those chunks to extract knowledge, and finally, storing this knowledge. It leverages a series of
    tools and agents, including GetText for reading files, intelligent_chunk for chunking text, LearnKGAgent for
    processing text chunks, and InjectKG.Consume for database injection.
    """
    def __init__(self):
        """
        Initializes the FileProcessor class with its required components.
        """
        self.logger = Logger(name=self.__class__.__name__)

        self.intelligent_chunk = intelligent_chunk
        self.get_text = GetText()
        self.learn_kg = LearnKGAgent()
        self.consumer = Consume()
        self.strip = Strip()
        self.store = StorageInterface()

    def process_file(self, knowledge_base_name: str, file_path: str) -> None:
        """
        Processes a single file through the pipeline, extracting text, chunking it, learning from the chunks,
        and injecting the learned knowledge into the knowledge base.

        Parameters:
            knowledge_base_name (str): The name of the knowledge base where the extracted information will be stored.
            file_path (str): The file path of the file to process.

        Returns:
            None

        This method sequentially performs the following steps:
            1. Reads text from the provided file.
            2. Chunks the text into smaller, more manageable pieces.
            3. Processes each chunk with the LearnKGAgent to learn and extract sentences.
            4. Each sentence is then processed for knowledge extraction.
            5. Extracted knowledge is injected into the knowledge base using the 'consume' method of the consumer tool.

        Errors at any stage are logged, and processing can optionally continue to the next chunk if an error occurs.
        The filename without its extension is used as the source name in the knowledge base entries.

        The method does not return a value but may print information about the injected knowledge entries
        and log errors.
        """
        filename_with_extension = os.path.basename(file_path)
        filename_without_extension, _ = os.path.splitext(filename_with_extension)

        try:
            # Step 1: Extract text from the file
            file_content = self.get_text.read_file(file_path)
            file_clean = self.strip.strip_invalid_chars(file_content)
        except Exception as e:
            self.logger.log(f"Error reading file: {e}", 'error')
            return

        try:
            # Step 2: Create chunks of the text
            chunks = self.intelligent_chunk(file_clean, chunk_size=2)
        except Exception as e:
            self.logger.log(f"Error chunking text: {e}", 'error')
            return

        for chunk in chunks:
            try:
                # Steps within the loop for learning and injecting data
                kg_results = self.store.storage_utils.query_memory(chunk)
                data = self.learn_kg.run(text_chunk=chunk, existing_knowledge=kg_results)

                if data is not None and 'sentences' in data and data['sentences']:
                    for key in data['sentences']:
                        sentence = data['sentences'][key]
                        reason = data['reasons'].get(key, "")

                        injected = self.consumer.consume(knowledge_base_name=knowledge_base_name,
                                                         sentence=sentence,
                                                         reason=reason,
                                                         source_name=filename_without_extension,
                                                         source_path=file_path,
                                                         chunk=chunk,
                                                         existing_knowledge=kg_results)
                        print(f"The following entry was added to the knowledge graph:\n{injected}\n\n")
                else:
                    self.logger.log("No relevant knowledge was found", 'info')
            except Exception as e:
                self.logger.log(f"Error processing chunk: {e}", 'error')
                continue  # Optionally continue to the next chunk
