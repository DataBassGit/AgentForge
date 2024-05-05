import re
from .Logger import Logger


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

    def __init__(self):
        """
        Initializes the PromptHandling class with a Logger instance.
        """
        self.logger = Logger(name=self.__class__.__name__)

    def extract_prompt_variables(self, template: str) -> list:
        """
        Extracts variable names from a prompt template.

        Parameters:
            template (str): The prompt template containing variables within curly braces.

        Returns:
            list: A list of variable names extracted from the template.

        Raises:
            Exception: Logs an error message if an exception occurs during the extraction process.
        """
        try:
            return re.findall(self.pattern, template)
        except Exception as e:
            self.logger.log(f"Error extracting prompt variables: {e}", 'error')
            return []

    def handle_prompt_template(self, prompt_template: str, data: dict) -> str:
        """
        Checks if all required variables in a prompt template are present and not empty in the provided data.
        Returns the template if conditions are met, or None otherwise.

        Parameters:
            prompt_template (str): The prompt template to check.
            data (dict): The data dictionary to check for required variables.

        Returns:
            str or None: The original prompt template if all variables are present and not empty, None otherwise.

        Raises:
            Exception: Logs an error message if an exception occurs during the process.
        """
        try:
            required_vars = self.extract_prompt_variables(prompt_template)

            if not required_vars:
                return prompt_template

            if all(data.get(var) for var in required_vars):
                return prompt_template
            return None
        except Exception as e:
            self.logger.log(f"Error handling prompt template: {e}", 'error')
            return None

    def render_prompt_template(self, template: str, data: dict) -> str:
        """
        Renders a prompt template by replacing each variable with its corresponding value from provided data.

        Parameters:
            template (str): The prompt template containing variables.
            data (dict): The data dictionary containing values for the variables in the template.

        Returns:
            str: The rendered template with variables replaced by their corresponding data values.

        Raises:
            Exception: Logs an error message if an exception occurs during the rendering process.
        """
        try:
            def replacement_function(match):
                variable_name = match.group(1)
                result = data.get(variable_name, match.group(0))
                return str(result)

            variable_pattern = re.compile(self.pattern)
            prompt = variable_pattern.sub(replacement_function, template)

            return prompt
        except Exception as e:
            self.logger.log(f"Error rendering prompt template: {e}", 'error')
            return template  # Optionally return the original template in case of failure
