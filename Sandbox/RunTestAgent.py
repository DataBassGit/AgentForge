from CustomAgents.TestAgent import TestAgent

test = TestAgent()

text = "Hi! I am testing your functionality, is everything nominal and in order from your point of view?"

result = test.run(text=text)

print(f"Agent Response: {result}")

