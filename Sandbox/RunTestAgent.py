from CustomAgents.TestAgent import TestAgent
from CustomAgents.TestoAgent import TestoAgent

test = TestAgent()

text = "Hi! I am testing your functionality, is everything nominal and in order from your point of view?"

result = test.run(text=text)

print(f"TestAgent Response: {result}")

testo = TestoAgent()

result = testo.run(text=text)

print(f"TestoAgent Response: {result}")

