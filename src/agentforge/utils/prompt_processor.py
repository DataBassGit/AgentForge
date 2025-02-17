import re
from agentforge.utils.logger import Logger

class PromptProcessor:
    """
    A utility class for handling dynamic prompt templates. It supports extracting variables from templates,
    checking for the presence of required variables in data, and rendering templates with values from provided data,
    including nested placeholders such as {agent_id.nested_key.sub_key}.
    """

    # Pattern to find all occurrences of {some_key} or {some_key.nested_key}
    # Explanation:
    #   - \{ and \} match literal curly braces
    #   - ([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)
    #       - [a-zA-Z_][a-zA-Z0-9_]* matches an initial variable name, e.g. "A1"
    #       - (?:\.[a-zA-Z_][a-zA-Z0-9_]*)* optionally allows dot notation for nested keys, e.g. ".answer.more"
    #
    pattern = r"\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}"

    def __init__(self):
        """
        Initializes the PromptHandling class with a Logger instance.
        """
        self.logger = Logger(name=self.__class__.__name__)

    ##################################################
    # Validation & Basic Checks
    ##################################################

    def check_prompt_format(self, prompts):
        """
        Checks if the prompts dictionary has the correct format.

        Parameters:
            prompts (dict): The dictionary containing the prompts.

        Raises:
            ValueError: If the prompts do not contain only 'system' and 'user' keys,
                        or if the sub-prompts are not dictionaries.
        """
        # Check if 'system' and 'user' are the only keys present
        if set(prompts.keys()) != {'system', 'user'}:
            error_message = (
                "Error: Prompts should contain only 'system' and 'user' keys. "
                "Please check the prompt YAML file format."
            )
            self.logger.log(error_message, 'error')
            raise ValueError(error_message)

        # Allow 'system' and 'user' prompts to be either dicts or strings
        for prompt_type in ['system', 'user']:
            prompt_value = prompts.get(prompt_type, {})
            if not isinstance(prompt_value, (dict, str)):
                error_message = (
                    f"Error: The '{prompt_type}' prompt should be either a string or a dictionary of sub-prompts."
                )
                self.logger.log(error_message, 'error')
                raise ValueError(error_message)

    ##################################################
    # Variable Extraction & Nested Lookups
    ##################################################

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

    @staticmethod
    def _nested_lookup(data: dict, path: str):
        """
        Performs a nested lookup in 'data' by splitting 'path' on dots.
        Returns None if any key isn't found along the way.

        Example:
            data = {"A2": {"answer": "42"}}, path = "A2.answer"
            -> returns "42"
        """
        keys = path.split('.')
        val = data
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return None
        return val

    ##################################################
    # Template Checking
    ##################################################

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
                return prompt_template  # no placeholders, so just return as is

            # For each required variable, ensure there's a non-empty value in data
            # if we do nested lookups, we check them individually
            for var in required_vars:
                val = self._nested_lookup(data, var)
                if not val:
                    return None
            return prompt_template
        except Exception as e:
            error_message = f"Error handling prompt template: {e}"
            self.logger.log(error_message, 'error')
            raise Exception(error_message)

    ##################################################
    # Template Rendering
    ##################################################

    def render_prompt_template(self, template: str, data: dict) -> str:
        """
        Renders a prompt template by replacing each variable with its corresponding value from provided data.
        Supports nested placeholders like {A2.answer}.

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
                variable_name = match.group(1)  # e.g. "A2.answer"
                val = self._nested_lookup(data, variable_name)
                # If val is None, we preserve the original placeholder.
                return str(val) if val is not None else match.group(0)

            variable_pattern = re.compile(self.pattern)
            # Perform variable substitution
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
        Renders the 'system' and 'user' prompts separately.

        Parameters:
            prompts (dict): The dictionary containing 'system' and 'user' prompts.
            data (dict): The data dictionary containing values for the variables.

        Returns:
            dict: A dictionary containing the rendered 'system' and 'user' prompts.

        Raises:
            Exception: Logs an error message and raises an exception if an error occurs during prompt rendering.
        """
        try:
            rendered_prompts = {}
            for prompt_type in ['system', 'user']:
                rendered_sections = []
                prompt_content = prompts.get(prompt_type, {})
                if isinstance(prompt_content, str):
                    prompt_sections = {'main': prompt_content}
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

