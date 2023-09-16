from neo4j import GraphDatabase


class Neo4jTripleManager:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the database connection."""
        self._driver.close()

    def inject_triple(self, subject, predicate, obj):
        """
        Inject a triple (subject, predicate, object) into the Neo4j database.
        """
        try:
            # Create the Cypher query
            query = (
                f"MERGE (s:Entity {{name: '{subject}'}}) "
                f"MERGE (o:Entity {{name: '{obj}'}}) "
                f"MERGE (s)-[:{predicate}]->(o)"
            )
            # Execute the query
            self._driver.session().run(query)
        except Exception as e:
            print(f"Error while injecting triple ({subject}, {predicate}, {obj}): {e}")
            return False
        return True

    def _create_triple(self, tx, subject, predicate, obj):
        query = (
            "MERGE (s:Node {name: $subject})"
            "MERGE (o:Node {name: $obj})"
            "MERGE (s)-[:RELATION {type: $predicate}]->(o)"
        )
        tx.run(query, subject=subject, predicate=predicate, obj=obj)

    def query_subject(self, subject):
        """Query the database for a subject and return related triples."""
        with self._driver.session() as session:
            result = session.execute_read(self._get_related_triples, subject)
            return result

    def _get_related_triples(self, tx, subject):
        query = (
            "MATCH (s:Node {name: $subject})-[r]->(o)"
            "RETURN s.name AS subject, r.type AS predicate, o.name AS object"
        )
        result = tx.run(query, subject=subject)
        return [{"subject": record["subject"],
                 "predicate": record["predicate"],
                 "object": record["object"]} for record in result]


# Usage:
uri = "bolt://localhost:12255"
user = "neo4j"
password = "secretgraph"

db = Neo4jTripleManager(uri, user, password)
db.inject_triple("Alice", "likes", "Bob")
triples = db.query_subject("Alice")
print(triples)

db.close()
