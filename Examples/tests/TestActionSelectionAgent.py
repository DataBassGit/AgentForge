from agentforge.agents.ActionSelectionAgent import ActionSelectionAgent

objective = "Create a batch file that can update a pip library as a test build, separate from the main distribution."
task = "Plan the Batch File: Outline the commands that will be included, such as activation of a virtual environment, installation or upgrading of the library, and any additional steps like running tests."

def extract_metadata(data):
    # extract the 'metadatas' key from results
    return data['metadatas'][0][0]


class TestAgent:

    def __init__(self):
        self.action_agent = ActionSelectionAgent()

    def test(self):
        self.action_agent.data = {'objective': objective, 'task': task}

        context = None
        frustration = 0.5
        action_results = self.action_agent.run(context=context, frustration=frustration)

        if 'documents' in action_results:
            action = extract_metadata(action_results)
            self.action_agent.functions.print_result(action['Description'], 'Action Selected')
        else:
            self.action_agent.functions.print_result(f'No Relevant Action Found! - Frustration: {frustration}', 'Selection Results')


if __name__ == '__main__':
    TestAgent().test()

