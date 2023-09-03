from agentforge.agent import Agent

import ast

from colorama import init
init(autoreset=True)


def extract_metadata(results):
    # extract the 'metadatas' key from results
    extracted_metadata = results['metadatas'][0][0]

    return extracted_metadata


class ActionPrimingAgent(Agent):

    def load_additional_data(self):
        self.data['task'] = self.functions.get_current_task()['document']

    def build_output(self):
        try:
            formatted_result = self.result.replace('\n', '').replace('\t', '')
            self.output = ast.literal_eval(formatted_result)
        except Exception as e:
            self.logger.log(self.result, 'error')
            raise ValueError(f"\n\nError while building output for agent: {e}")

    def save_result(self):
        pass

