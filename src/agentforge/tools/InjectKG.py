"""
This will receive the following:
Sentence - Sentence to be added to the KG
Reason - Reason the sentence is important
Source name - Name of the document it originated from
Source URL - Path ot the source document at generation

It will then use TripleExtract to generate a subject predicate object from the sentence and return:
Subject
Object
Predicate

These will be entered into the knowledge graph collection on the database. The Sentence will be the document, the other
six parameters will be metadata.
"""
from agentforge.agents.MetadataKGAgent import MetadataKGAgent
from agentforge.utils.storage_interface import StorageInterface
import uuid


class Consume:

    def __init__(self):
        self.trip = MetadataKGAgent()
        self.storage = StorageInterface().storage_utils

    def consume(self, sentence, reason, source_name, source_url, chunk=None):
        # Extract Triples

        nodes = self.trip.run(sentence = sentence, chunk=chunk)

        # build params
        random_uuid = uuid.uuid4()
        params = {
            "collection_name": "knowledge_graph",
            "data": [sentence],
            "ids": [f"{random_uuid}"],
            "metadata": [{
                "id": f"{random_uuid}",
                "reason": reason,
                "sentence": sentence,
                "source_name": source_name,
                "source_url": source_url,
                **nodes
            }]
        }

        output = params.copy()
        metadata_values = output["metadata"][0]  # Access the first (and only) metadata item

        # Print each metadata item on its own line
        for key, value in metadata_values.items():
            print(f"{key}: {value}")
        self.storage.save_memory(**params)
        return output

