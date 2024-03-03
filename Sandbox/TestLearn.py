from agentforge.modules.LearnDoc import FileProcessor

# filepath = "2307.03172.pdf"
filepath = "Reflexion - Language Agents with Verbal Reinforcement Learning.txt"


def learn_file(file_path):
    fp = FileProcessor()
    fp.process_file(file_path)


if __name__ == "__main__":
    learn_file(filepath)
