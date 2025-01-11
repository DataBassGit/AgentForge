from agentforge.cogarch import CogArch

test = CogArch(name="simple")
text = "Hi! I am testing your functionality, is everything nominal and in order from your point of view?"

result = test.run(text=text)
print(f"Test Flow Response: {result}")

