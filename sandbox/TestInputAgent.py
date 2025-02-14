from agentforge.agent import Agent

def main():
    # Instantiate the EchoAgent using its YAML prompt file
    agent = Agent('fine_tune')

    print("Model is awaiting your input...")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Chao!")
            break

        response = agent.run(user_input=user_input)
        print("\n---------\nAgent:\n", response)

if __name__ == "__main__":
    main()