from agentforge.loops.ActionExecution import Action

objective = "Create a batch file that can update a pip library as a test build, separate from the main distribution."
task = "Plan the Batch File: Outline the commands that will be included, such as activation of a virtual"\
        "environment, installation or upgrading of the library, and any additional steps like running tests."


class TestAction:

    def __init__(self):
        self.action = Action()

    def test(self):
        self.action.data = {'objective': objective, 'task': task, 'tool': task}
        self.action.run(None, frustration=0.5)


if __name__ == '__main__':
    TestAction().test()

