import spacy
import sys


def download_spacy_model(model_name):
    """
    Download a SpaCy model using SpaCy's CLI
    """
    print(f"Downloading the {model_name} model...")
    spacy.cli.download(model_name)
    print(f"Model {model_name} downloaded successfully.")


# Attempt to load the English model
spacy_model_name = "en_core_web_sm"

try:
    nlp = spacy.load(spacy_model_name)
except OSError:
    # Model not found, attempt to download it
    download_spacy_model(spacy_model_name)
    try:
        # Reload the model after downloading
        nlp = spacy.load(spacy_model_name)
    except OSError:
        print(f"Failed to load model {spacy_model_name} after downloading.", file=sys.stderr)
        sys.exit(1)


class TripleExtract:
    @staticmethod
    def find_subject_predicate_object(_sentence):
        doc = nlp(_sentence)
        _subject = None
        _predicate = None
        _object = None

        for token in doc:
            # Finding the subject
            if "subj" in token.dep_:
                _subject = token.text
            # Finding the predicate (verb)
            if "VERB" in token.pos_:
                _predicate = token.text
            # Finding the object
            if "obj" in token.dep_:
                _object = token.text

        # print(f"Debug Trip:\n\nSubject: {_subject}\nPredicate: {_predicate}\nObject: {_object}")
        return _subject, _predicate, _object
