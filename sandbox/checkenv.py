import os


def print_env_variables():
    print("Environment Variables:")
    for key, value in os.environ.items():
        print(f"{key}: {value}")

    # Print specific variables we're interested in
    print("\nSpecific Variables:")
    specific_vars = ['BRAIN_CHANNEL', 'DISCORD_TOKEN', 'OPENAI_API_KEY', 'BRAVE_API_KEY', 'GROQ_API_KEY']
    for var in specific_vars:
        print(f"{var}: {os.getenv(var)}")

if __name__ == "__main__":
    print_env_variables()
