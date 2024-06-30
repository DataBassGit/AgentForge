from CustomAgents.DocsAgent import DocsAgent
from agentforge.utils.chroma_utils import ChromaUtils

docs_agent = DocsAgent()
storage = ChromaUtils('dignity')
while True:
    user_input = input("Welcome to the chat with docs!\nQuestion: ")
    docs = storage.query_memory(collection_name="docs", query=user_input, num_results=50)
    response = docs_agent.run(docs=docs['documents'], query=user_input)
    print(f"Agent: {response}")
