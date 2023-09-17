from agentforge.modules.ActionExecution import Action

objective = "Create a batch file that can update a pip library as a test build, separate from the main distribution."
task = "Plan the Batch File: Outline the commands that will be included, such as activation of a virtual"\
        "environment, installation or upgrading of the library, and any additional steps like running tests."
selected_action = {
    "Name": "Create File",
    "Description": "This action first uses the 'Read Directory' tool to display the structure of a directory, then utilizes the 'Write File' tool to write or append text to a specified file in a given directory. It offers the flexibility to either create a new file or append to an existing one.",
    "Example": "print_directory_structure = print_directory(directory, max_depth=3); response = write_file('path/to/folder', 'filename.txt', 'This is the content', mode='a')",
    "Instruction": "Start by using the 'Read Directory' tool to view the structure of a directory, specifying a dictionary that represents the directory structure and an optional depth. Then, to create or modify a file, specify the target folder, the desired filename, and the content you wish to write. Optionally, provide a mode ('a' for append and 'w' for overwrite) to determine how the content should be added to the file.",
    "Tools": "Read Directory, Write File"
}

# selected_action = {
#   "Name": "Web Search",
#   "Description": "This action performs a Google search from a query, scrapes the text from one of the returned URLs, and then breaks the scraped text into manageable chunks.",
#   "Example": "search_results = google.google_search(query, number_result); url = search_results[2][0]; scrapped = web_scrape.get_plain_text(url)",
#   "Instruction": "First, use the 'Google Search' tool to perform a Google search and retrieve a list of search results. Choose a URL from the search results, then use the 'Web Scrape' tool to scrape the text from that URL.",
#   "Tools": "Google Search, Web Scrape"
# }


class TestAction:

    def __init__(self):
        self.action = Action()

    def test(self):
        self.action.data = {'objective': objective, 'task': task, 'tool': task}
        result = self.action.run(selected_action)


if __name__ == '__main__':
    TestAction().test()

