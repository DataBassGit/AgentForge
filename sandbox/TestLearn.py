from agentforge.modules.LearnDoc import FileProcessor

filepath = "./ThisIsYou.txt"  # Path to TXT/PDF File to Consume


def learn_file(file_path):
    fp = FileProcessor()
    fp.process_file(knowledge_base_name='knowledge_base', file_path=file_path)


if __name__ == "__main__":
    learn_file(filepath)
