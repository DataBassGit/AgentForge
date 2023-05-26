from .agent import Agent


class HeuristicReflectionAgent(Agent):
    def __init__(self):
        super().__init__("HeuristicReflectionAgent", log_level="info")

    def parse_output(self, result, botid, data):
        # criteria = result.split("MEETS CRITERIA: ")[1].split("\n")[0].lower()
        # edit = result.split("RECOMMENDED EDIT: ")[1].split("\n")[0].lower()
        # response = result.split("RESPONSE: ")[1].strip()

        if "MEETS CRITERIA: " in result:
            criteria = result.split("MEETS CRITERIA: ")[1].split("\n")[0].lower()
        else:
            criteria = "n/a"
            # Handle the case when "RESPONSE: " is not in the result
            print("Unable to find 'MEETS CRITERIA: ' in the result string")

        if "RECOMMENDED EDIT: " in result:
            edit = result.split("RECOMMENDED EDIT: ")[1].strip()
        else:
            edit = "No recommended edits found."
            # Handle the case when "RESPONSE: " is not in the result
            print("Unable to find 'RECOMMENDED EDIT: ' in the result string")

        if "RESPONSE: " in result:
            response = result.split("RESPONSE: ")[1].strip()
        else:
            response = "No Response"
            # Handle the case when "RESPONSE: " is not in the result
            print("Unable to find 'RESPONSE: ' in the result string")

        return {'criteria': criteria, 'edit': edit, 'response': response,
                'botid': botid, 'data': data}
