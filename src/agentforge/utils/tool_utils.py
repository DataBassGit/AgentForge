# utils/functions/tool_utils.py
import traceback
import importlib
import shlex
from typing import List, Union
from agentforge.utils.logger import Logger
from typing import Any, Dict

from agentforge.storage.chroma_storage import ChromaStorage


class ToolUtils:
    """
    A utility class for dynamically interacting with tools. It supports dynamically importing tool modules,
    executing specified commands within those modules, and handling tool priming for display purposes.

    Attributes:
        logger (Logger): Logger instance for logging messages.
    """

    BUILTIN_FUNCTIONS = {
        "print": print,
        "len": len,
        "sum": sum,
        "max": max,
        "min": min,
        # Add more built-in functions if needed
    }

    def __init__(self, docker_container=None):
        """
        Initializes the ToolUtils class with a Logger instance.
        """
        self.logger = Logger(name=self.__class__.__name__)
        self.storage = ChromaStorage.get_or_create(storage_id="tool_library")
        self.docker_container = docker_container

    # --------------------------------------------------------------------------------------------------------
    # ----------------------------------------- Dynamic Tool Methods -----------------------------------------
    # --------------------------------------------------------------------------------------------------------

    def dynamic_tool(self, tool: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dynamically loads a tool module and executes a specified command within it, using arguments provided in the
        payload. Supports original python script calls and the new SKILLS standard (CLI execution).

        Parameters:
            tool (dict): The tool or skill definition.
            payload (dict): A dictionary containing the 'command' to be executed and 'args' for the command.

        Returns:
            dict: The result of executing the command, or an error dictionary if an error occurs.
        """
        tool_module = tool.get("Script") or tool.get("script")
        tool_class = tool.get("Class") or tool.get("class")
        command = payload.get("command") or tool.get("Command") or tool.get("command")
        args = payload.get("args", {})

        try:
            if tool_module:
                if command is None:
                    raise ValueError("Tool payload must include a command")
                self.logger.info(f"\nRunning Python Tool {tool_class or tool_module} ...")
                result = self._execute_tool(tool_module, tool_class, command, args)
            else:
                self.logger.info(f"\nRunning Skill {tool.get('Name', 'Unknown')} ...")
                result = self._execute_skill(tool, command, args)

            self.logger.log(f"\nResult:\n{result}", "info", "Actions")
            return {"status": "success", "data": result}
        except (AttributeError, TypeError, Exception) as e:
            return self._handle_error(e, str(tool_module), str(tool_class), str(command))

    def _execute_tool(self, tool_module: str, tool_class: str | None, command: str, args: Dict[str, Any]) -> Any:
        """
        Executes the specified command within the tool module natively.

        Note: Python tools execute locally rather than in Docker because they require
        access to the host's Python environment, imported libraries, and framework state.
        Security-wise, this is safe because it only invokes pre-defined internal functions,
        unlike CLI skills which execute shell commands.
        """
        if tool_module in self.BUILTIN_FUNCTIONS:
            command_func = self.BUILTIN_FUNCTIONS[tool_module]  # type: ignore
            result = command_func(**args)
        else:
            if tool_module.startswith(".agentforge"):
                # Remove '.agentforge' from the beginning of the path
                relative_path = tool_module.replace(".agentforge", "", 1)
                tool = importlib.import_module(relative_path, package="agentforge")
            else:
                tool = importlib.import_module(tool_module)

            if tool_class and hasattr(tool, tool_class):
                tool_instance = getattr(tool, tool_class)()
                command_func = getattr(tool_instance, command)
            else:
                command_func = getattr(tool, command)

            result = command_func(**args)

        return result

    def _execute_skill(self, tool: Dict[str, Any], command: str | None, args: Union[Dict[str, Any], List, str]) -> Any:
        """
        Executes a CLI-based skill from a SKILLS.md definition.
        """
        commands = []
        prereqs = tool.get("prerequisites", {})
        if isinstance(prereqs, dict) and "commands" in prereqs:
            commands = prereqs["commands"]

        # Determine the base executable
        if command:
            base_cmd = command
        elif commands:
            base_cmd = commands[0]
        else:
            raise ValueError(f"No executable command found for skill '{tool.get('Name')}'.")

        cmd_list = [base_cmd]

        # Build command line arguments safely
        if isinstance(args, dict):
            for k, v in args.items():
                if str(v).lower() == "false":
                    continue
                prefix = "-" if len(k) == 1 else "--"
                cmd_list.append(f"{prefix}{k}")
                if str(v).lower() != "true":
                    cmd_list.append(str(v))
        elif isinstance(args, list):
            cmd_list.extend([str(a) for a in args])
        elif isinstance(args, str):
            cmd_list.extend(shlex.split(args))

        self.logger.info(f"Executing Skill Command: {' '.join(cmd_list)}")

        # Route execution strictly to Docker
        if not self.docker_container:
            raise RuntimeError(
                "A persistent Docker container is required to execute CLI skills securely. "
                "Local execution fallback has been disabled."
            )

        self.logger.info(f"Routing execution to persistent Docker container: {self.docker_container.name}")
        try:
            exit_code, output = self.docker_container.exec_run(cmd_list)
            if exit_code != 0:
                decoded_output = output.decode("utf-8", errors="replace")
                error_msg = f"Docker command failed with exit code {exit_code}.\nOutput: {decoded_output}"
                raise RuntimeError(error_msg)
            return output.decode("utf-8", errors="replace") or "Command executed successfully in Docker with no output."
        except Exception as e:
            raise RuntimeError(f"Docker execution failed: {e}")

    def _handle_error(self, e: Exception, tool_module: str, tool_class: str, command: str) -> Dict[str, Any]:
        """
        Handles errors encountered during command execution.

        Parameters:
            e (Exception): The exception raised.
            tool_module (str): The tool module where the error occurred.
            tool_class (str): The class within the tool module where the error occurred.
            command (str): The command that caused the error.

        Returns:
            dict: An error dictionary with the error message and traceback.
        """
        if isinstance(e, AttributeError):
            error_message = (
                f"Tool '{tool_module}' does not have a class named '{tool_class}' or command named '{command}'."
                f"\nError: {e}"
            )
        elif isinstance(e, TypeError):
            error_message = f"Error passing arguments: {e}"
        else:
            error_message = f"Error executing command: {e}"

        self.logger.error(error_message)
        return {"status": "failure", "message": error_message, "traceback": traceback.format_exc()}

    # --------------------------------------------------------------------------------------------------------
    # ------------------------------------ Parsing and Formatting Methods ------------------------------------
    # --------------------------------------------------------------------------------------------------------

    @staticmethod
    def format_item(item: Dict[str, Union[str, List[str]]], order: List[str] | None = None) -> str:
        """
        Formats an item (action or tool) into a human-readable string.

        Parameters:
            item (Dict[str, Union[str, List[str]]]): The item to format.
            order (Optional[List[str]]): The order in which to format the item's keys.

        Returns:
            str: The formatted item string.
        """
        if order is None:
            order = list(item.keys())

        formatted_string = ""
        for key in order:
            if key in item:
                value = item[key]
                if isinstance(value, list):
                    formatted_list = "\n- ".join([str(items).strip() for items in value])
                    formatted_string += f"{key}:\n- {formatted_list}\n\n"
                elif isinstance(value, str):
                    if len(value.splitlines()) > 1:
                        formatted_string += f"{key}:\n{value.strip()}\n\n"
                    else:
                        formatted_string += f"{key}: {value.strip()}\n"
        return formatted_string.strip()

    def format_item_list(self, items: Dict, order: List[str] | None = None) -> str | None:
        """
        Formats the actions into a human-readable string based on a given order and stores it in the agent's data for
        later use.

        Parameters:
            items (Dict): The list of actions or tools to format.
            order (Optional[List[str]]): The order in which to format the action's keys.

        Returns:
            Optional[str]: The formatted string of actions, or None if an error occurs.
        """
        try:
            formatted_actions = []
            for item_name, metadata in items.items():
                formatted_action = self.format_item(metadata, order)
                formatted_actions.append(formatted_action)
            return "---\n" + "\n---\n".join(formatted_actions) + "\n---"
        except Exception as e:
            self.logger.error(f"Error Formatting Item List:\n{items}\n\nError: {e}")
            return None
