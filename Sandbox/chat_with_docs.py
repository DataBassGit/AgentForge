from customagents.DocsAgent import DocsAgent
from agentforge.utils.chroma_utils import ChromaUtils


# Create an agent
docs_agent = DocsAgent()
storage = ChromaUtils()


# Function to chat with documents
def chat_with_docs():
    while True:
        user_input = input("Welcome to the chat with docs! Type 'exit' to quit.\nYou: ")
        if user_input.lower() == 'exit':
            break

        # Query data
        docs = storage.query_memory(collection_name="docs", query=user_input, num_results=5)
        print(f"\nDocs: \n{docs['documents']}\n")

        # Process user input and get response
        response = docs_agent.run(docs=docs['documents'], query=user_input)
        print(f"Agent: {response}")


if __name__ == "__main__":
    chat_with_docs()
