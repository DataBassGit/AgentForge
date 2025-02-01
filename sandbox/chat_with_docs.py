from agentforge.agent import Agent
from agentforge.storage.chroma_storage import ChromaStorage

docs_agent = Agent(agent_name="DocsAgent")
kb = ChromaStorage()

while True:
    user_input = input("Welcome to the chat with docs!\nQuestion: ")
    results = kb.query_memory(collection_name="docs", query=user_input, num_results=5)
    print(results)
    response = docs_agent.run(docs=results['documents'], query=user_input, whatever='data')
    print(f"Agent: {response}")
    # print(f"Results: {results}")
