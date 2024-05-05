from agentforge.agents.MetadataKGAgent import MetadataKGAgent
from agentforge.utils.storage_interface import StorageInterface
import uuid
from typing import Optional, Any, Dict


class Consume:

    def __init__(self):
        self.metadata_extract = MetadataKGAgent()
        self.storage = StorageInterface().storage_utils

    def consume(self, knowledge_base_name: str, sentence: str, reason: str, source_name: str, source_path: str,
                chunk: Optional[Any] = None, existing_knowledge: Optional[str] = None) -> Dict[str, Any]:
        """
        Process and store a given sentence along with its metadata in a specified knowledge base.

        This method extracts triples and other relevant metadata from the given sentence,
        generates a unique identifier, builds a parameter dictionary with the sentence and its metadata,
        and then saves this information using the storage's save_memory method.
        Finally, it prints and returns the constructed parameters.

        Parameters:
            knowledge_base_name (str): The name of the knowledge base collection to store the data.
            sentence (str): The sentence to be processed and stored.
            reason (str): The reason or context for storing this sentence.
            source_name (str): The name of the source from which the sentence is derived.
            source_path (str): The path of the source from which the sentence is derived.
            chunk (Optional[Any]): Additional optional chunk data to be used in triple extraction, defaults to None.
            existing_knowledge (Optional[Any]): Additional existing knowledge to be used in triple extraction,
                defaults to None.

        Returns:
            Dict[str, Any]: A dictionary containing the input data along with the generated metadata.
        """

        # Extract Metadata
        nodes = self.metadata_extract.run(sentence=sentence, text_chunk=chunk, existing_knowledge=existing_knowledge)

        # build params
        random_uuid = str(uuid.uuid4())
        params = {
            "collection_name": knowledge_base_name,
            "data": [sentence],
            "ids": [f"{random_uuid}"],
            "metadata": [{
                "id": f"{random_uuid}",
                "reason": reason,
                "sentence": sentence,
                "source_name": source_name,
                "source_path": source_path,
                **nodes
            }]
        }

        # Output preparation and printing
        output = params.copy()
        metadata_values = output["metadata"][0]  # Access the first (and only) metadata item
        if isinstance(metadata_values, dict):
            for key, value in metadata_values.items():
                print(f"{key}: {value}")
        else:
            print("Error: metadata_values is not a dictionary")

        # Saving the data
        self.storage.save_memory(**params)

        return output

