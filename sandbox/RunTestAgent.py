from agentforge.agent import Agent

test = Agent(agent_name="TestAgent")
text = "Hi! I am testing your functionality, is everything nominal and in order from your point of view?"

result = test.run(text=text)
print(f"TestAgent Response: {result}")

