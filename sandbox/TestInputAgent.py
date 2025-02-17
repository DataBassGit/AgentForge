from agentforge.agent import Agent

def main():
    # Instantiate the EchoAgent using its YAML prompt file
    agent = Agent('InputAgent')

    print("Model is awaiting your input...")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Chao!")
            break

        user_dict = {"input_agent":{"user_input": user_input}}

        response = agent.run(**user_dict)
        print(f"---------\n{response}\n---------")

if __name__ == "__main__":
    main()



