import re


class PromptHandling:

    def handle_prompt_type(self, prompts, prompt_type):
        """Handle each type of prompt and return template and vars."""
        prompt_data = prompts.get(prompt_type, {})
        required_vars = self.extract_prompt_variables(prompt_data)
        if prompt_data:
            return [(prompt_data, required_vars)]
        return []

    def remove_prompt_if_none(self, prompts, kwargs):
        prompts_copy = prompts.copy()

        for prompt_type, prompt_data in prompts_copy.items():
            required_vars = self.extract_prompt_variables(prompt_data)

            # If there are no required vars we keep the prompt and skip to the next iteration
            if not required_vars:
                continue

            # Remove the prompt if the required vars don't exist or if any is empty
            for var in required_vars:
                if not kwargs.get(var):
                    prompts.pop(prompt_type)
                    break  # Exit this loop, the dictionary has been changed

    @staticmethod
    def render_template(template, variables, data):
        temp = template.format(
            **{k: v for k, v in data.items() if k in variables}
        )

        return temp

    @staticmethod
    def extract_prompt_variables(template):
        # Regular expression to match valid Python variable names inside {}
        pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
        return re.findall(pattern, template)
