'''
This will receive the following:
Sentence - Sentence to be added to the KG
Reason - Reason the sentence is important
Source name - Name of the document it originated from
Source URL - Path ot the source document at generation

It will then use TripleExtract to generate a subject predicate object from the sentence and return:
Subject
Object
Predicate

These will be entered into the knowledgegraph collection on the database. The Sentence will be the document, the other
six paramenters will be metadata.
'''

from agentforge.tools.TripleExtract import TripleExtract
from agentforge.utils.storage_interface import StorageInterface
import uuid

class Consume:

    def __init__(self):
        self.trip = TripleExtract()
        self.storage = StorageInterface().storage_utils

    def consume(self, sentence, reason, sourcename, sourceurl):
        # Extract Triples
        subject, predicate, object_ = self.trip.find_subject_predicate_object(sentence)

        # build params
        random_uuid = uuid.uuid4()
        params = {
            "collection_name": "knowledgegraph",
            "data": [sentence],
            "ids": [f"{random_uuid}"],
            "metadata": [{
                "id": f"{random_uuid}",
                "reason": reason,
                "sentence": sentence,
                "sourcename": sourcename,
                "sourceurl": sourceurl,
                "subject": subject,
                "predicate": predicate,
                "object": object_,
            }]
        }
        self.storage.save_memory(params)
        return params


if __name__ == "__main__":
    sentences = [
        "Alice sang a beautiful song.",
        "With great enthusiasm, the students discussed the novel intensely.",
        "The old man at the store bought a new hat.",
        "Under the bright moonlight, the cat prowled silently.",
        "The teacher gave the students homework.",
        "In the garden, the birds were chirping melodiously."
        # Add more sentences as needed
    ]
    reasons = "Because I wanna"
    sourcenames = "Oobabooga Github"
    sourceurls = "https://github.com/oobabooga/text-generation-webui"

    for sent in sentences:
        consumer = Consume()
        results = consumer.consume(sent, reasons, sourcenames, sourceurls)
