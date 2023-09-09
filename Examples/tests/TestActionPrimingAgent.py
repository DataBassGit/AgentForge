from agentforge.agents.ActionPrimingAgent import ActionPrimingAgent
from agentforge.utils.function_utils import Functions

objective = "Create a batch file that can update a pip library as a test build, separate from the main distribution."
task = "Plan the Batch File: Outline the commands that will be included, such as activation of a virtual environment, installation or upgrading of the library, and any additional steps like running tests."
tool = "Name: Web Scrape\nArgs: url (str)\nCommand: get_plain_text\nDescription: The 'Web Scrape' tool is used to pull all text from a webpage. Simply provide the web address (URL), and the tool will return the webpage's content in plain text.\nExample: scrapped = get_plain_text(url)\nInstruction: The 'get_plain_text' method of the 'Web Scrape' instance takes a URL as an input, which represents the webpage to scrape. It returns the textual content of that webpage as a string. You can send only one URL, so if you receive more than one, choose the most likely URL to contain the results you expect."
tool_name = "Web Scrape"
tool_result = None


def extract_metadata(data):
    # extract the 'metadatas' key from results
    return data['metadatas'][0][0]


class TestAgent:

    def __init__(self):
        # Summarize the Search Results
        self.priming_agent = ActionPrimingAgent()
        self.functions = Functions()

    def test(self):
        self.priming_agent.data = {'objective': objective, 'task': task, 'tool': task}

        payload = self.priming_agent.run(tool=tool, results=tool_result)

        self.functions.print_primed_tool(tool_name, payload)


if __name__ == '__main__':
    TestAgent().test()

