import re
from agentforge.utils.Logger import Logger


class PromptHandling:
    """
    A utility class for handling dynamic prompt templates. It supports extracting variables from templates,
    checking for the presence of required variables in data, and rendering templates with values from provided data.

    Attributes:
        pattern (str): A regular expression pattern to find all occurrences of variables within curly braces
        in templates.
    """

    # Define a pattern to find all occurrences of {variable_name}
    pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}"
    # pattern = r"(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})"
    # pattern = r"(?<!\\)\{([a-zA-Z_][a-zA-Z0-9_]*)\}"

    def __init__(self):
        """
        Initializes the PromptHandling class with a Logger instance.
        """
        self.logger = Logger(name=self.__class__.__name__)

    def check_prompt_format(self, prompts):
        """
        Checks if the prompts dictionary has the correct format.

        Parameters:
            prompts (dict): The dictionary containing the prompts.

        Raises:
            ValueError: If the prompts do not contain only 'System' and 'User' keys,
                        or if the sub-prompts are not dictionaries.
        """
        # Check if 'System' and 'User' are the only keys present
        if set(prompts.keys()) != {'System', 'User'}:
            error_message = (
                "Error: Prompts should contain only 'System' and 'User' keys. "
                "Please check the prompt YAML file format."
            )
            self.logger.log(error_message, 'error')
            raise ValueError(error_message)

        # Allow 'System' and 'User' prompts to be either dicts or strings
        for prompt_type in ['System', 'User']:
            prompt_value = prompts.get(prompt_type, {})
            if not isinstance(prompt_value, (dict, str)):
                error_message = (
                    f"Error: The '{prompt_type}' prompt should be either a string or a dictionary of sub-prompts."
                )
                self.logger.log(error_message, 'error')
                raise ValueError(error_message)

    def extract_prompt_variables(self, template: str) -> list:
        """
        Extracts variable names from a prompt template.

        Parameters:
            template (str): The prompt template containing variables within curly braces.

        Returns:
            list: A list of variable names extracted from the template.

        Raises:
            Exception: Logs an error message and raises an exception if an error occurs during the extraction process.
        """
        try:
            return re.findall(self.pattern, template)
        except Exception as e:
            error_message = f"Error extracting prompt variables: {e}"
            self.logger.log(error_message, 'error')
            raise Exception(error_message)

    def handle_prompt_template(self, prompt_template: str, data: dict) -> str | None:
        """
        Checks if all required variables in a prompt template are present and not empty in the provided data.
        Returns the template if conditions are met, or None otherwise.

        Parameters:
            prompt_template (str): The prompt template to check.
            data (dict): The data dictionary to check for required variables.

        Returns:
            str or None: The original prompt template if all variables are present and not empty, None otherwise.

        Raises:
            Exception: Logs an error message and raises an exception if an error occurs during the process.
        """
        try:
            required_vars = self.extract_prompt_variables(prompt_template)

            if not required_vars:
                return prompt_template

            if all(data.get(var) for var in required_vars):
                return prompt_template
            return None
        except Exception as e:
            error_message = f"Error handling prompt template: {e}"
            self.logger.log(error_message, 'error')
            raise Exception(error_message)

    def render_prompt_template(self, template: str, data: dict) -> str:
        """
        Renders a prompt template by replacing each variable with its corresponding value from provided data.

        Parameters:
            template (str): The prompt template containing variables.
            data (dict): The data dictionary containing values for the variables in the template.

        Returns:
            str: The rendered template with variables replaced by their corresponding data values.

        Raises:
            Exception: Logs an error message and raises an exception if an error occurs during the rendering process.
        """
        try:
            def replacement_function(match):
                variable_name = match.group(1)
                result = data.get(variable_name, match.group(0))
                return str(result)

            variable_pattern = re.compile(self.pattern)
            # First, perform variable substitution
            prompt = variable_pattern.sub(replacement_function, template)

            # Then, unescape any escaped braces
            prompt = self.unescape_braces(prompt)

            return prompt
        except Exception as e:
            error_message = f"Error rendering prompt template: {e}"
            self.logger.log(error_message, 'error')
            raise Exception(error_message)

    def render_prompts(self, prompts, data):
        """
        Renders the 'System' and 'User' prompts separately.

        Parameters:
            prompts (dict): The dictionary containing 'System' and 'User' prompts.
            data (dict): The data dictionary containing values for the variables.

        Returns:
            dict: A dictionary containing the rendered 'System' and 'User' prompts.

        Raises:
            Exception: Logs an error message and raises an exception if an error occurs during prompt rendering.
        """
        try:
            rendered_prompts = {}
            for prompt_type in ['System', 'User']:
                rendered_sections = []
                prompt_content = prompts.get(prompt_type, {})
                if isinstance(prompt_content, str):
                    prompt_sections = {'Main': prompt_content}
                else:
                    prompt_sections = prompt_content

                for prompt_name, prompt_template in prompt_sections.items():
                    template = self.handle_prompt_template(prompt_template, data)
                    if template:
                        rendered_prompt = self.render_prompt_template(template, data)
                        rendered_sections.append(rendered_prompt)
                    else:
                        self.logger.log(
                            f"Skipping '{prompt_name}' in '{prompt_type}' prompt due to missing variables.",
                            'info'
                        )
                # Join the rendered sections into a single string for each prompt type
                final_prompt = '\n'.join(rendered_sections)
                rendered_prompts[prompt_type] = final_prompt
            return rendered_prompts
        except Exception as e:
            error_message = f"Error rendering prompts: {e}"
            self.logger.log(error_message, 'error')
            raise Exception(error_message)

    def validate_rendered_prompts(self, rendered_prompts):
        """
        Validates the rendered prompts to ensure none are empty.

        Parameters:
            rendered_prompts (dict): A dictionary containing the rendered prompts.

        Raises:
            ValueError: If any of the prompts are empty strings after rendering.
        """
        for prompt_type, prompt_content in rendered_prompts.items():
            if not prompt_content.strip():
                error_message = (
                    f"Error: The '{prompt_type}' prompt is empty after rendering. "
                    f"Please check your prompt templates and data."
                )
                self.logger.log(error_message, 'error')
                raise ValueError(error_message)

    @staticmethod
    def unescape_braces(template: str) -> str:
        """
        Replaces all instances of /{.../} with {...} in the template.

        Parameters:
            template (str): The prompt template containing escaped braces.

        Returns:
            str: The template with escaped braces unescaped.
        """
        return re.sub(r'/\{(.*?)/}', r'{\1}', template)
