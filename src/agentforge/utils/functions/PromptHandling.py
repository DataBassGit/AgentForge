import re


class PromptHandling:
    # Define a pattern to find all occurrences of {variable_name}
    pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"

    def extract_prompt_variables(self, template):
        try:
            # Regular expression to match valid Python variable names inside {}
            return re.findall(self.pattern, template)
        except Exception as e:
            # Log or print the error message
            print(f"Error extracting prompt variables: {e}")
            return []

    def handle_prompt_template(self, prompt_template, data):
        """Return the template if all its required variables are present in the data and are not empty."""
        try:
            required_vars = self.extract_prompt_variables(prompt_template)

            if not required_vars:
                return prompt_template

            if all(data.get(var) for var in required_vars):
                return prompt_template
            return None
        except Exception as e:
            # Log or print the error message
            print(f"Error handling prompt template: {e}")
            return None

    def render_prompt_template(self, template, data):
        """Replace each variable in the template with its value from data"""
        try:
            def replacement_function(match):
                variable_name = match.group(1)
                result = data.get(variable_name, match.group(0))
                return str(result)

            variable_pattern = re.compile(self.pattern)
            prompt = variable_pattern.sub(replacement_function, template)

            return prompt
        except Exception as e:
            # Log or print the error message
            print(f"Error rendering prompt template: {e}")
            return template  # Optionally return the original template in case of failure
