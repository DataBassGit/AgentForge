import spacy
import sys

def download_spacy_model(model_name):
    """
    Download a SpaCy model using SpaCy's CLI.

    Args:
        model_name (str): The name of the SpaCy model to download.

    Raises:
        Exception: If the download fails.
    """
    try:
        print(f"Downloading the {model_name} model...")
        spacy.cli.download(model_name)
        print(f"Model {model_name} downloaded successfully.")
    except Exception as e:
        raise Exception(f"Failed to download model {model_name}: {str(e)}")

# Attempt to load the English model
spacy_model_name = "en_core_web_trf"

try:
    nlp = spacy.load(spacy_model_name)
except OSError:
    # Model not found, attempt to download it
    try:
        download_spacy_model(spacy_model_name)
        nlp = spacy.load(spacy_model_name)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

class TripleExtract:
    """
    A class for extracting subject-predicate-object triples from sentences.
    """

    @staticmethod
    def find_subject_predicate_object(sentence):
        """
        Extract subject, predicate, and object from a given sentence.

        Args:
            sentence (str): The input sentence.

        Returns:
            tuple: A tuple containing (subject, predicate, object), each as a string or None if not found.

        Raises:
            ValueError: If the input is not a string or is empty.
            Exception: For any other unexpected errors during processing.
        """
        if not isinstance(sentence, str) or not sentence.strip():
            raise ValueError("Input sentence must be a non-empty string")

        try:
            doc = nlp(sentence)
            subject, predicate, _object = None, None, None

            # Identify named entities using SpaCy NER
            for entity in doc.ents:
                if entity.label_ in ("PERSON", "ORG"):
                    # Prioritize named entities as potential subjects
                    subject = entity
                    break

            # Use syntactic dependency labels to identify subject and verb
            for token in doc:
                if token.dep_ == "nsubj" or token.dep_ == "nsubjpass":
                    subject = token
                elif token.pos_ == "VERB":
                    # Check if it's part of a verb phrase indicating the predicate
                    if token.dep_ == "aux" and nlp(token.head.text).pos_ == "VERB":
                        continue  # Skip auxiliary verbs
                    else:
                        predicate = token.head  # Consider the head of the verb phrase as the predicate
                        break

            # If subject not found directly, explore other possibilities
            if not subject:
                if predicate:
                    # Check for subject within relative clauses
                    for child in predicate.children:
                        if child.dep_ == "relcl":
                            subject = TripleExtract.find_subject_in_clause(child)
                            if subject:
                                break
                else:
                    # Try finding a verb phrase as the subject
                    for chunk in doc.noun_chunks:
                        if any(token.pos_ == "VERB" for token in chunk):
                            subject = chunk
                            break

            # Look for candidate objects after finding subject and predicate
            if subject and predicate:
                for child in predicate.children:
                    if child.dep_ in ["dobj", "attr", "iobj"]:  # Include indirect objects
                        _object = child
                    elif child.dep_ == "prep":
                        # Iterate over children and check for "pobj" dependency
                        for grandchild in child.children:
                            if grandchild.dep_ == "pobj":
                                _object = grandchild
                                break  # Stop iterating after finding "pobj"

            # Convert identified tokens to text if they exist
            subject_text = subject.text if subject else None
            predicate_text = predicate.lemma_ if predicate else None  # Using lemma for base form of verb
            object_text = _object.text if _object else None

            print(
                f"Debug Trip:\n\nSentence: {sentence}\nSubject: {subject_text}\nPredicate: {predicate_text}\nObject: {object_text}")
            return subject_text, predicate_text, object_text  # Return the identified elements

        except Exception as e:
            raise Exception(f"An error occurred while processing the sentence: {str(e)}")

    @staticmethod
    def find_subject_in_clause(clause):
        """
        Find the subject in a given clause.

        Args:
            clause (spacy.tokens.Span): A SpaCy span representing a clause.

        Returns:
            spacy.tokens.Token or None: The subject token if found, None otherwise.
        """
        for token in clause:
            if token.dep_ in ["nsubj", "nsubjpass"]:
                return token
        return None

    @staticmethod
    def find_subject_predicate_object_with_chunk(sentence, chunk):
        """
        Extract subject, predicate, and object from a sentence, using a chunk for context.

        Args:
            sentence (str): The input sentence.
            chunk (str): A chunk of text providing context.

        Returns:
            tuple: A tuple containing (subject, predicate, object), each as a string or None if not found.

        Raises:
            ValueError: If the input sentence or chunk is not a string or is empty.
            Exception: For any other unexpected errors during processing.
        """
        if not isinstance(sentence, str) or not sentence.strip():
            raise ValueError("Input sentence must be a non-empty string")
        if not isinstance(chunk, str) or not chunk.strip():
            raise ValueError("Input chunk must be a non-empty string")

        try:
            doc = nlp(chunk)  # Process the chunk for context
            sentence_doc = nlp(sentence)  # Process the sentence separately

            # Identify named entities using SpaCy NER
            entities = [ent for ent in doc.ents if ent.label_ in ("PERSON", "ORG")]

            subject, predicate, _object = None, None, None

            # Use syntactic dependency labels to identify subject and verb
            for token in sentence_doc:
                if token.dep_ == "nsubj" or token.dep_ == "nsubjpass":
                    subject = token

                    # Filter irrelevant words based on POS tags and additional stop words
                    if subject and isinstance(subject, spacy.tokens.Doc):
                        filtered_subject_words = [
                            word.text
                            for word in subject.words
                            if word.pos_ not in ["STOP", "ADP", "DET", "AUX"]  # Add AUX for auxiliary verbs
                        ]
                    else:
                        filtered_subject_words = [subject.text] if subject else None

                    # Join the filtered words with a space
                    subject_text = " ".join(filtered_subject_words) if filtered_subject_words else None
                    print(f"\nDEBUG CHUNK: \nFiltered subject words: {filtered_subject_words}\nSubject text: {subject_text}\n")

                elif token.pos_ == "VERB":
                    # Check if it's part of a verb phrase indicating the predicate
                    if token.dep_ == "aux" and nlp(token.head.text).pos_ == "VERB":
                        continue  # Skip auxiliary verbs
                    else:
                        predicate = token.head  # Consider the head of the verb phrase as the predicate
                        break

            # If subject not found directly, explore other possibilities
            if not subject:
                if predicate:
                    # Check for subject within relative clauses or previous entities
                    for child in predicate.children:
                        if child.dep_ == "relcl":
                            subject = TripleExtract.find_subject_in_clause_with_chunk(child,
                                                                                      entities.copy())  # Pass a copy of entities
                            if subject:
                                break
                        elif child.dep_ == "pobj" and len(entities) > 0:
                            # Check if object from previous sentence is the subject
                            for entity in entities:
                                if entity.text == child.text:
                                    subject = entity
                                    break
                        else:
                            # Try finding a verb phrase as the subject
                            for chunk in doc.noun_chunks:
                                if any(token.pos_ == "VERB" for token in chunk):
                                    subject = chunk
                                    break

            # Look for candidate objects after finding subject and predicate
            if subject and predicate:
                for child in predicate.children:
                    if child.dep_ in ["dobj", "attr", "iobj"]:
                        for grandchild in child.children:  # Iterate over child.children
                            if grandchild.dep_ == "pobj":
                                _object = grandchild
                                break  # Stop iterating after finding the object
                    elif child.dep_ == "prep":
                        for grandchild in child.children:
                            if grandchild.dep_ == "pobj":
                                _object = grandchild
                                break  # Stop iterating after finding the object

            # Convert identified tokens to text if they exist
            subject_text = subject.text if subject else None
            predicate_text = predicate.lemma_ if predicate else None  # Using lemma for base form of verb
            object_text = _object.text if _object else None

            print(
                f"usingContext:\nSubject: {subject_text}\nPredicate: {predicate_text}\nObject: {object_text}")
            return subject_text, predicate_text, object_text

        except Exception as e:
            raise Exception(f"An error occurred while processing the sentence with chunk: {str(e)}")

    @staticmethod
    def find_subject_in_clause_with_chunk(clause, entities):
        """
        Find the subject in a given clause, considering entities from the context.

        Args:
            clause (spacy.tokens.Span): A SpaCy span representing a clause.
            entities (list): A list of named entities from the context.

        Returns:
            spacy.tokens.Token or spacy.tokens.Span or None: The subject if found, None otherwise.
        """
        for token in clause:
            if token.dep_ in ["nsubj", "nsubjpass"]:
                # Check if subject matches an entity from previous sentence
                for entity in entities:
                    if entity.text == token.text:
                        return token
                return token  # Found subject within clause
            elif token.pos_ == "PRON":  # Check pronouns within relative clause
                for ent in entities:
                    if ent.text == token.text:
                        return ent  # Pronoun referring to previous entity
        return None  # No subject found in clause or previous entities

# Usage example (commented out)
# if __name__ == "__main__":
#     try:
#         sentence = "The quick brown fox jumps over the lazy dog."
#         subject, predicate, obj = TripleExtract.find_subject_predicate_object(sentence)
#         print(f"Subject: {subject}")
#         print(f"Predicate: {predicate}")
#         print(f"Object: {obj}")
#     except Exception as e:
#         print(f"Error: {str(e)}")
