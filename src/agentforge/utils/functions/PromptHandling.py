class PromptHandling:
    @staticmethod
    def handle_prompt_type(prompts, prompt_type):
        """Handle each type of prompt and return template and vars."""
        prompt_data = prompts.get(prompt_type, {})
        if prompt_data:
            return [(prompt_data['template'], prompt_data['vars'])]
        return []

    @staticmethod
    def remove_prompt_if_none(prompts, kwargs):
        prompts_copy = prompts.copy()
        for prompt_type, prompt_data in prompts_copy.items():
            required_vars = prompt_data.get('vars', [])
            # If there are no required vars or all vars are empty, we keep the prompt
            if not required_vars or all(not var for var in required_vars):
                continue
            for var in required_vars:
                if kwargs.get(var) is None:
                    prompts.pop(prompt_type)
                    break  # Exit this loop, the dictionary has been changed

    @staticmethod
    def render_template(template, variables, data):
        temp = template.format(
            **{k: v for k, v in data.items() if k in variables}
        )

        return temp
