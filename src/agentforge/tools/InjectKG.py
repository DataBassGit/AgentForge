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

from agentforge.tools.TripleExtract import TripleExtract
from agentforge.utils.storage_interface import StorageInterface
import uuid


class Consume:

    def __init__(self):
        self.trip = TripleExtract()
        self.storage = StorageInterface().storage_utils

    def consume(self, sentence, reason, source_name, source_url):
        # Extract Triples
        _subject, _predicate, _object = self.trip.find_subject_predicate_object(sentence)

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
                "subject": _subject,
                "predicate": _predicate,
                "object": _object,
            }]
        }

        output = params.copy()

        self.storage.save_memory(params)
        return output

