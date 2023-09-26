from neo4j import GraphDatabase
from neo_utils import Neo4jTripleManager as neoutil

def main():

    uri = "bolt://localhost:12255"
    user = "neo4j"
    password = "secretgraph"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))

    list = [
        ("The USS Enterprise", "is", "a Galaxy-class Federation starship"),
        ("Captain Kirk", "serves as captain of", "the USS Enterprise"),
        ("Mr. Spock", "is", "First Officer on the USS Enterprise"),
        ("Warp drive", "allows", "starships to travel faster than light"),
        ("Transporters", "can beam", "people and objects between locations"),
        ("Tricorders", "are handheld devices that", "scan and record data"),
        ("Communicators", "enable", "voice communication over long distances"),
        ("Starfleet Academy", "trains", "Federation officers"),
        ("Klingons", "are", "an alien warrior race"),
        ("The Prime Directive", "prohibits Starfleet personnel from", "interfering with other cultures"),
        ("Vulcans", "value", "logic and emotional control"),
        ("The Borg", "aim to", "assimilate other beings into their collective"),
        ("Deep Space Nine", "is", "a space station near the planet Bajor"),
        ("Lieutenant Uhura", "works as", "the communications officer on the USS Enterprise"),
        ("The holodeck", "generates", "immersive holographic environments"),
        ("Photon torpedoes", "are", "high-energy projectile weapons"),
        ("Wesley Crusher", "was", "an acting Ensign aboard the Enterprise"),
        ("Captain Picard", "likes drinking", "Earl Grey tea"),
        ("Captain Picard", "is", "a Starfleet officer"),
    ]

    db = neoutil(uri, user, password)

    # Inject the triples
    for subject, predicate, obj in triples:
        success = db.inject_triple(subject, predicate, obj)
        if success:
            print(f"Injected triple: {subject} - {predicate} - {obj}")
        else:
            print(f"Failed to inject triple: {subject} - {predicate} - {obj}")

    # Close the database connection
    db.close()


if __name__ == "__main__":
    main()