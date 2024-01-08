from agentforge.modules.LearnDoc import FileProcessor


class TestModule:

    def __init__(self):
        self.module = FileProcessor()


if __name__ == '__main__':
    file = ("D:/Github/AgentForge/Examples/KG/Files/Chain-of-Thought Prompting Elicits Reasoning in Large Language "
            "Models.pdf")

    TestModule().module.process_file(file)


