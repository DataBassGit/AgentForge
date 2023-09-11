from agentforge.loops.ActionExecution import Action

objective = "Create a batch file that can update a pip library as a test build, separate from the main distribution."
task = "Plan the Batch File: Outline the commands that will be included, such as activation of a virtual"\
        "environment, installation or upgrading of the library, and any additional steps like running tests."
selected_action = {
    "Description": "This action utilizes the 'Write File' tool to write or append text to a specified file in a given directory. It offers the flexibility to either create a new file or append to an existing one.",
    "Example": "response = write_file('path/to/folder', 'filename.txt', 'This is the content', mode='a')",
    "Instruction": "To create or modify a file, specify the target folder, the desired filename, and the content you wish to write. Optionally, provide a mode ('a' for append and 'w' for overwrite) to determine how the content should be added to the file.",
    "Name": "Create File",
    "Tools": "Write File",
}


class TestAction:

    def __init__(self):
        self.action = Action()

    def test(self):
        self.action.data = {'objective': objective, 'task': task, 'tool': task}
        result = self.action.run(selected_action)


if __name__ == '__main__':
    TestAction().test()

