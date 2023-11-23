import spacy

# Load the English model
nlp = spacy.load("en_core_web_sm")

def find_subject_predicate_object(sentence):
    doc = nlp(sentence)
    subject = None
    predicate = None
    object_ = None

    for token in doc:
        # Finding the subject
        if "subj" in token.dep_:
            subject = token.text
        # Finding the predicate (verb)
        if "VERB" in token.pos_:
            predicate = token.text
        # Finding the object
        if "obj" in token.dep_:
            object_ = token.text

    return subject, predicate, object_

# Test the function with different sentences
sentences = [
    "Alice sang a beautiful song.",
    "With great enthusiasm, the students discussed the novel intensely.",
    "The old man at the store bought a new hat.",
    "Under the bright moonlight, the cat prowled silently.",
    "The teacher gave the students homework.",
    "In the garden, the birds were chirping melodiously."
    # Add more sentences as needed
]

for sentence in sentences:
    subject, predicate, object_ = find_subject_predicate_object(sentence)
    print(f"Sentence: '{sentence}'\nSubject: {subject}, Predicate: {predicate}, Object: {object_}\n")