from CustomAgents.DocsAgent import DocsAgent

docs_agent = DocsAgent()
# kb = ChromaUtils()

# user_input = input("Welcome to the chat with docs!\nQuestion: ")
user_input = 'Welcome to the chat with docs!'
results = "No results!"
# results = kb.query_memory(collection_name="docs", query=user_input, num_results=5)
print(results)
# response = docs_agent.run(docs=results['documents'], query=user_input, whatever='data')
response = docs_agent.run(docs=results, query=user_input, whatever='data')
print(f"Agent: {response}")
# print(f"Results: {results}")
