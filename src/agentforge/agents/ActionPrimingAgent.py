from agentforge.agent import Agent
from ast import literal_eval as leval


def extract_outermost_brackets(s):
    count = 0
    start_idx = None
    end_idx = None

    for idx, char in enumerate(s):
        if char == '{':
            count += 1
            if count == 1:
                start_idx = idx
        elif char == '}':
            count -= 1
            if count == 0 and start_idx is not None:
                end_idx = idx
                break

    if start_idx is not None and end_idx is not None:
        return s[start_idx:end_idx + 1]
    else:
        return None


class ActionPrimingAgent(Agent):

    def build_output(self):
        try:
            formatted_result = self.get_formatted_result()
            self.output = leval(formatted_result)
        except Exception as e:
            self.logger.log(self.result, 'error')
            raise ValueError(f"\n\nError while building output for agent: {e}")

    def get_formatted_result(self):
        result = self.result.replace('\n', '').replace('\t', '')
        return extract_outermost_brackets(result)

    def load_additional_data(self):
        self.data['task'] = self.functions.get_current_task()['document']

    def save_result(self):
        pass
