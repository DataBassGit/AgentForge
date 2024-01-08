from agentforge.tools.GetText import GetText


class TestTool:

    def __init__(self):
        self.tool = GetText()

    def test(self):
        file_content = self.tool.read_file("D:/Github/AgentForge/Examples/KG/Files/Chain-of-Thought Prompting Elicits "
                                           "Reasoning in Large Language Models.pdf")
        print(file_content)


if __name__ == '__main__':
    TestTool().test()

