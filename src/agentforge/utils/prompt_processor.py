import re
from typing import Any, Mapping, Sequence, Iterable, Tuple, Callable
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
        self.logger = Logger(name=self.__class__.__name__, default_logger=self.__class__.__name__.lower())

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
            self.logger.error(error_message)
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
            self.logger.error(error_message)
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
                if val is not None:
                    formatted_val = self.value_to_markdown(val)
                    # Detect indentation before the placeholder
                    start = match.start()
                    # Find the start of the line
                    line_start = template.rfind('\n', 0, start) + 1
                    indent = template[line_start:start]
                    # Apply indentation to all lines except the first
                    lines = formatted_val.split('\n')
                    if len(lines) > 1:
                        lines = [lines[0]] + [indent + line if line.strip() else line for line in lines[1:]]
                    return '\n'.join(lines).strip()
                else:
                    return match.group(0)


            variable_pattern = re.compile(self.pattern)
            # Perform variable substitution
            prompt = variable_pattern.sub(replacement_function, template)

            # Then, unescape any escaped braces
            prompt = self.unescape_braces(prompt)

            return prompt
        except Exception as e:
            error_message = f"Error rendering prompt template: {e}"
            self.logger.error(error_message)
            raise Exception(error_message)

    def render_prompts(self, prompts, data):
        """
        Renders the 'system' and 'user' prompts separately and validates that they are not empty.

        Parameters:
            prompts (dict): The dictionary containing 'system' and 'user' prompts.
            data (dict): The data dictionary containing values for the variables.

        Returns:
            dict: A dictionary containing the rendered 'system' and 'user' prompts.

        Raises:
            Exception: Logs an error message and raises an exception if an error occurs during prompt rendering.
            ValueError: If any of the rendered prompts are empty strings.
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
                        self.logger.info(
                            f"Skipping '{prompt_name}' in '{prompt_type}' prompt due to missing variables."
                        )
                # Join the rendered sections into a single string for each prompt type
                final_prompt = '\n'.join(rendered_sections)
                rendered_prompts[prompt_type] = final_prompt
            
            # Validate rendered prompts before returning
            self._validate_rendered_prompts(rendered_prompts)
            
            return rendered_prompts
        except Exception as e:
            error_message = f"Error rendering prompts: {e}"
            self.logger.error(error_message)
            raise Exception(error_message)

    def _validate_rendered_prompts(self, rendered_prompts):
        """
        Internal method to validate the rendered prompts to ensure none are empty.

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
                self.logger.error(error_message)
                raise ValueError(error_message)

    def build_persona_markdown(self, static_content, persona_settings):
        """
        Build markdown representation of static persona content for system prompt injection.
        Truncate if exceeds character cap from settings.
        
        Args:
            static_content (dict): Dictionary containing static content from persona
            persona_settings (dict): Dictionary containing persona settings
            
        Returns:
            str: Markdown formatted representation of persona static content
        """
        if not static_content:
            return None
            
        # Use the centralized markdown formatting helper
        persona_md = self.value_to_markdown(static_content)
        
        # Get character cap from settings - treat 0 as no cap
        if hasattr(persona_settings, 'static_char_cap'):
            static_char_cap = getattr(persona_settings, 'static_char_cap', 8000)
        elif isinstance(persona_settings, dict):
            static_char_cap = persona_settings.get('static_char_cap', 8000)
        else:
            static_char_cap = 8000
        
        # Only truncate if cap is greater than 0 and persona_md exceeds the cap
        if static_char_cap > 0 and len(persona_md) > static_char_cap:
            self.logger.warning(
                f"Persona markdown exceeds character cap ({len(persona_md)} > {static_char_cap}). "
                f"Truncating to {static_char_cap} characters."
            )
            persona_md = persona_md[:static_char_cap] + "..."
        
        return persona_md

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

    ##################################################
    # Value Formatting
    ##################################################

    def value_to_markdown(self, val: Any, indent: int = 0) -> str:
        """Render a dict, list, or scalar into minimalist Markdown."""
        pad = "  " * indent     # two-space indent per level

        if isinstance(val, Mapping):
            segments = []
            for k, v in val.items():
                if isinstance(v, (Mapping, Sequence)) and not isinstance(v, str):
                    segments.append(f"{pad}{k}:")
                    segments.append(self.value_to_markdown(v, indent + 1))
                else:
                    segments.append(f"{pad}{k}: {v}")
            return "\n".join(segments)

        if isinstance(val, Sequence) and not isinstance(val, str):
            segments = []
            for item in val:
                if isinstance(item, (Mapping, Sequence)) and not isinstance(item, str):
                    segments.append(f"{pad}- {self.value_to_markdown(item, indent + 1)}")
                else:
                    segments.append(f"{pad}- {item}")
            return "\n".join(segments)

        return f"{pad}{val}"
