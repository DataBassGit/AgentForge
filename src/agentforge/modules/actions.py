import os
import re
import yaml
import traceback
from typing import Any, List, Dict, Union, cast
from agentforge.agent import Agent
from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.config import Config
from agentforge.utils.tool_utils import ToolUtils


def id_generator(data: List[Dict]) -> List[str]:
    """
    Generates a list of string IDs for the given data.

    Parameters:
        data (List[Dict]): The data for which to generate IDs.

    Returns:
        List[str]: A list of generated string IDs.
    """
    return [str(i + 1) for i in range(len(data))]


class Actions:
    """
    Provides a series of methods for developers to create custom solutions for managing and executing actions and tools
    within the framework. This class offers the necessary flexibility and modularity to support both in-depth custom
    implementations and generic examples.

    The `auto_execute` method serves as a comprehensive example of how to use the provided methods to orchestrate the
    flow from loading action-specific tools, executing these tools, to injecting the processed data into the knowledge
    graph. Developers can use this method directly or reference it to build their own tailored workflows.
    """

    # --------------------------------------------------------------------------------------------------------
    # -------------------------------- Constructor and Initialization Methods --------------------------------
    # --------------------------------------------------------------------------------------------------------

    def __init__(self, chroma_instance):
        """
        Initializes the Actions class, setting up logger, storage utilities, and loading necessary components for
        action processing.

        Parameters:
            chroma_instance: An active instance of ChromaStorage to use for memory operations.
        """
        # Initialize the logger, storage, and functions
        self.logger = Logger(name=self.__class__.__name__)
        self.config = Config()
        self.storage = chroma_instance

        # Initialize persistent Docker container for skills execution
        self.docker_container = self._initialize_docker_container()

        self.tool_utils = ToolUtils(docker_container=self.docker_container)
        self.parsing_utils = ParsingProcessor()

        # Initialize the agents
        self.action_creation = Agent("ActionCreationAgent")
        self.action_selection = Agent("ActionSelectionAgent")
        self.priming_agent = Agent("ToolPrimingAgent")

        # Load the actions and tools from the config
        self.actions = self.initialize_collection("Actions")
        self.tools = self.initialize_collection("Tools")

        # Load skills recursively from the skills directory
        self.skills = self.load_all_skills()

    # --------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Helper Methods ---------------------------------------------
    # --------------------------------------------------------------------------------------------------------

    def _initialize_docker_container(self):
        """
        Initializes a persistent Docker container to be used for executing CLI-based skills securely.
        """
        try:
            import docker  # type: ignore[reportMissingModuleSource]

            client = docker.from_env()
            container_name = "agentforge_skills_env"

            try:
                # Try to attach to an existing container
                container = client.containers.get(container_name)
                if container.status != "running":
                    container.start()
                self.logger.log(f"Attached to existing Docker container: {container_name}", "info", "Actions")
                return container
            except docker.errors.NotFound:  # type: ignore[reportAttributeAccessIssue]
                # Create a new persistent container holding an idle baseline image
                self.logger.log(f"Creating new persistent Docker container: {container_name}", "info", "Actions")
                container = client.containers.run(
                    "ubuntu:latest",  # Can be customized via system settings in the future
                    command="tail -f /dev/null",  # Keeps the container running
                    name=container_name,
                    detach=True,
                )
                return container
        except ImportError:
            self.logger.log(
                "Docker python package (docker) not installed. CLI skills execution is completely disabled.",
                "error",
                "Actions",
            )
            return None
        except Exception as e:
            self.logger.log(
                f"Failed to initialize persistent Docker container: {e}. CLI skills execution is completely disabled.",
                "error",
                "Actions",
            )
            return None

    def initialize_collection(self, collection_name: str) -> Dict[str, Dict]:
        """
        Initializes a specified collection in the vector database with preloaded data. Mainly used to load the
        actions and tools data into the database, allowing for semantic search.

        Parameters:
            collection_name (str): The name of the collection to initialize.

        Returns:
            Dict[str, Dict]: A dictionary where keys are item names and values are item details.
        """
        item_list = {}
        data = self.config.data[collection_name.lower()]
        ids = id_generator(data)

        for (key, value), act_id in zip(data.items(), ids):
            value["ID"] = act_id
            item_list[value["Name"]] = value

        description = [value["Description"] for value in item_list.values()]
        metadata = [{"Name": key} for key, value in item_list.items()]

        # Save the item into the selected collection
        self.storage.save_memory(collection_name=collection_name, data=description, ids=ids, metadata=metadata)
        self.logger.log(f"\n{collection_name} collection initialized", "info", "Actions")

        return item_list

    def load_all_skills(self) -> Dict[str, Dict]:
        """
        Recursively searches for and loads all SKILL.md and SKILLS.md files within the
        .agentforge/skills directory.

        Returns:
            Dict[str, Dict]: A dictionary of all loaded skills/tools.
        """
        all_skills = {}
        # Resolve the path to .agentforge/skills
        skills_dir = os.path.join(str(self.config.config_path), "skills")

        if not os.path.isdir(skills_dir):
            self.logger.log(f"Skills directory not found at '{skills_dir}'. Skipping skill load.", "info", "Actions")
            return all_skills

        # Search recursively using os.walk
        for subdir, dirs, files in os.walk(skills_dir):
            for file in files:
                if file in ["SKILL.md", "SKILLS.md"]:
                    file_path = os.path.join(subdir, file)
                    skills = self.load_skills_from_markdown(file_path)
                    if skills:
                        all_skills.update(skills)

        return all_skills

    def load_skills_from_markdown(self, file_path: str) -> Dict[str, Dict]:
        """
        Loads tools/skills from a markdown file to populate the Tools collection.
        Parses YAML frontmatter as metadata and the markdown body as instructions.

        Parameters:
            file_path (str): Path to the SKILLS.md file.

        Returns:
            Dict[str, Dict]: A dictionary of loaded skills/tools.
        """
        if not os.path.exists(file_path):
            self.logger.log(f"Skills file '{file_path}' not found. Skipping.", "info", "Actions")
            return {}

        item_list = {}
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            # Regex to extract YAML frontmatter
            frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)

            if frontmatter_match:
                yaml_content = frontmatter_match.group(1)
                markdown_body = frontmatter_match.group(2).strip()
                try:
                    parsed_metadata = yaml.safe_load(yaml_content) or {}
                except Exception as e:
                    self.logger.log(f"Error parsing YAML frontmatter in '{file_path}': {e}", "error", "Actions")
                    parsed_metadata = {}
            else:
                parsed_metadata = {}
                markdown_body = content

            if not parsed_metadata:
                self.logger.log(f"No valid YAML frontmatter found in '{file_path}'.", "warning", "Actions")
                return {}

            name = parsed_metadata.get("name", parsed_metadata.get("Name", f"Skill_{os.path.basename(file_path)}"))
            description = parsed_metadata.get("description", parsed_metadata.get("Description", ""))

            skill_id = f"skill_{str(name).replace(' ', '_').lower()}"

            # Base skill data
            skill_data = {"ID": skill_id, "Name": name, "Description": description, "Instruction": markdown_body}

            # Merge the rest of the YAML frontmatter into skill_data
            for k, v in parsed_metadata.items():
                if k.lower() == "example":
                    continue  # Deprecate 'example' metadata field
                if k not in skill_data:
                    skill_data[k] = v

            item_list[name] = skill_data

            # Prepare metadata for ChromaDB (must be primitive types: str, int, float, bool)
            chroma_meta = {}
            for k, v in skill_data.items():
                if isinstance(v, (str, int, float, bool)):
                    chroma_meta[k] = v
                elif v is None:
                    chroma_meta[k] = ""
                else:
                    chroma_meta[k] = str(v)  # Flatten arrays/dicts to string to prevent Chroma errors

            # Description is the actual document stored for vector search
            doc_text = description if description else str(name)

            # Save the item into the Skills collection
            self.storage.save_memory(collection_name="Skills", data=[doc_text], ids=[skill_id], metadata=[chroma_meta])
            self.logger.log(f"\nSkills collection updated with skill '{name}' from {file_path}", "info", "Actions")

        except Exception as e:
            self.logger.log(f"Error loading skills from {file_path}: {e}", "error", "Actions")

        return item_list

    def get_relevant_items_for_objective(
        self,
        collection_name: str,
        objective: str,
        threshold: float | None = None,
        num_results: int = 1,
        parse_result: bool = True,
    ) -> Dict[str, Dict]:
        """
        Loads items (actions or tools) based on the current objective and specified criteria.

        Parameters:
            collection_name (str): The name of the collection to search in ('Actions' or 'Tools').
            objective (str): The objective to find relevant items for.
            threshold (Optional[float]): The threshold for item relevance (Lower is stricter).
            num_results (int): The number of results to return. Default is 1.
            parse_result (bool): Whether to parse the result. Default is True.
                If False, returns the results as they come from the database.
                If True, parses the results to include only items that are loaded in the system.

        Returns:
            Dict[str, Dict]: The item list or an empty dictionary if no items are found.
        """
        item_list = {}
        try:
            item_list = self.storage.search_storage_by_threshold(
                collection_name=collection_name, query=objective, threshold=threshold, num_results=num_results
            )
        except Exception as e:
            self.logger.log(f"Error loading {collection_name.lower()}: {e}", "error", "Actions")

        # "checking tools first, then skills" for vector search integration
        if collection_name.lower() == "tools":
            try:
                skill_list = self.storage.search_storage_by_threshold(
                    collection_name="Skills", query=objective, threshold=threshold, num_results=num_results
                )
                if skill_list and skill_list.get("metadatas"):
                    if not item_list or not item_list.get("metadatas"):
                        item_list = skill_list
                    else:
                        item_list["metadatas"].extend(skill_list["metadatas"])
                        if "distances" in item_list and "distances" in skill_list:
                            item_list["distances"].extend(skill_list["distances"])
                        if "documents" in item_list and "documents" in skill_list:
                            item_list["documents"].extend(skill_list["documents"])

                        # Sort combined results by distance to keep relevance accurate
                        if "distances" in item_list:
                            combined = list(
                                zip(item_list["distances"], item_list["metadatas"], item_list.get("documents", []))
                            )
                            combined.sort(key=lambda x: x[0])
                            item_list["distances"] = [x[0] for x in combined]
                            item_list["metadatas"] = [x[1] for x in combined]
                            if "documents" in item_list:
                                item_list["documents"] = [x[2] for x in combined]
            except Exception as e:
                self.logger.log(f"Error loading skills for objective: {e}", "error", "Actions")

        if not item_list or not item_list.get("metadatas"):
            self.logger.log(f"No {collection_name} Found", "info", "Actions")
            return {}

        if parse_result:
            parsed_item_list = {}
            for metadata in item_list.get("metadatas", []):
                item_name = metadata.get("Name")
                if collection_name.lower() == "tools":
                    # Check tools first, then skills
                    if item_name in self.tools:
                        parsed_item_list[item_name] = self.tools[item_name]
                    elif hasattr(self, "skills") and item_name in self.skills:
                        parsed_item_list[item_name] = self.skills[item_name]
                else:
                    target_collection = getattr(self, collection_name.lower(), {})
                    if item_name in target_collection:
                        parsed_item_list[item_name] = target_collection[item_name]
            item_list = parsed_item_list

        return item_list

    def get_tools_in_action(self, action: Dict) -> List[Dict] | Dict[str, str] | None:
        """
        Loads the tools specified in the action's configuration.

        Parameters:
            action (Dict): The action containing the tools to load.

        Returns:
            Optional[List[Dict]]: A list with the loaded tools or None.

        Raises:
            Exception: If an error occurs while loading action tools.
        """
        try:
            tools = []
            for tool_name in action.get("Tools", []):
                # Checking tools first, then skills
                if tool_name in self.tools:
                    tools.append(self.tools[tool_name])
                elif hasattr(self, "skills") and tool_name in self.skills:
                    tools.append(self.skills[tool_name])
                else:
                    raise KeyError(f"Tool or Skill '{tool_name}' not found")
        except Exception as e:
            error_message = f"Error in loading tools from action '{action.get('Name', 'Unknown')}': {e}"
            self.logger.log(error_message, "error", "Actions")
            tools = {"error": error_message, "traceback": traceback.format_exc()}

        return tools

    # --------------------------------------------------------------------------------------------------------
    # ----------------------------------- Primary Module (Agents) Methods ------------------------------------
    # --------------------------------------------------------------------------------------------------------

    def select_action_for_objective(
        self, objective: str, action_list: Union[str, Dict], context: str | None = None, parse_result: bool = True
    ) -> Union[str, Dict, None]:
        """
        Selects an action for the given objective from the provided action list.

        Parameters:
            objective (str): The objective to select an action for.
            action_list (Union[str, Dict]): The list of actions to select from.
                If given a Dict, the method will attempt to convert to a string.
            context (Optional[str]): The context for action selection.
            parse_result (bool): Whether to parse the result. Default is True.

        Returns:
            Union[str, Dict]: The selected action or formatted result.
        """
        if isinstance(action_list, dict):
            action_list = self.tool_utils.format_item_list(action_list) or ""

        selected_action = self.action_selection.run(objective=objective, action_list=action_list, context=context)
        if selected_action is None:
            return None

        if parse_result:
            selected_action = self.parsing_utils.parse_by_format(str(selected_action), "yaml")

        return selected_action

    def craft_action_for_objective(
        self, objective: str, tool_list: Union[Dict, str], context: str | None = None, parse_result: bool = True
    ) -> Union[str, Dict, None]:
        """
        Crafts a new action for the given objective.

        Parameters:
            objective (str): The objective to craft an action for.
            tool_list (Union[Dict, str]): The list of tools to be used.
                Will attempt to convert to a string if given a Dict.
            context (Optional[str]): The context for action crafting.
            parse_result (bool): Whether to parse the result. Default is True.

        Returns:
            Union[str, Dict]: The crafted action or formatted result.
        """
        if isinstance(tool_list, dict):
            tool_list = self.tool_utils.format_item_list(tool_list) or ""

        new_action = self.action_creation.run(objective=objective, context=context, tool_list=tool_list)
        if new_action is None:
            return None

        if parse_result:
            new_action = self.parsing_utils.parse_by_format(str(new_action), "yaml")

            if new_action is None:
                msg = {"error": "Error Creating Action"}
                self.logger.log(msg["error"], "error", "Actions")
                return msg

        return new_action

    def prime_tool_for_action(  # noqa: PLR0913 - legacy public helper call shape
        self,
        objective: str,
        action: Union[str, Dict],
        tool: Dict,
        previous_results: str | None = None,
        tool_context: str | None = None,
        action_info_order: List[str] | None = None,
        tool_info_order: List[str] | None = None,
    ) -> Dict:
        """
        Prepares the tool for execution by running the ToolPrimingAgent.

        Parameters:
            objective (str): The objective for tool priming.
            action (Union[str, Dict]): The action to prime the tool for.
                If a dictionary, it will be formatted using the tool_info_order methods.
            tool (Dict): The tool to be primed.
            previous_results (Optional[str]): The results from previous tool executions.
            tool_context (Optional[str]): The context for the tool.
            action_info_order (Optional[List[str]]): The order of action information to include in the Agent prompt.
            tool_info_order (Optional[List[str]]): The order of tool information to include in the Agent prompt.

        Returns:
            Dict: The formatted payload for the tool.

        Raises:
            Exception: If an error occurs during tool priming.
        """
        formatted_tool = self.tool_utils.format_item(tool, tool_info_order)

        if isinstance(action, dict):
            action = self.tool_utils.format_item(action, action_info_order)

        try:
            # Load the paths into a dictionary
            paths_dict = self.storage.config.settings.system.paths

            # Construct the work_paths string by iterating over the dictionary
            work_paths = None
            if paths_dict:
                work_paths = "\n".join(f"{key}: {value}" for key, value in paths_dict.items())

            payload = self.priming_agent.run(
                objective=objective,
                action=action,
                tool_name=tool.get("Name"),
                tool_info=formatted_tool,
                path=work_paths,
                previous_results=previous_results,
                tool_context=tool_context,
            )

            formatted_payload = self.parsing_utils.parse_by_format(str(payload or ""), "yaml")

            if not isinstance(formatted_payload, dict):
                return {"error": "Parsing Error - Model did not respond in specified format"}

            self.logger.log(f"Tool Payload: {formatted_payload}", "info", "Actions")
            return cast(Dict[str, Any], formatted_payload)
        except Exception as e:
            message = f"Error in priming tool '{tool['Name']}': {e}"
            self.logger.log(message, "error", "Actions")
            return {"error": message, "traceback": traceback.format_exc()}

    def run_tools_in_sequence(
        self,
        objective: str,
        action: Dict,
        action_info_order: List[str] | None = None,
        tool_info_order: List[str] | None = None,
    ) -> Dict | None:
        """
        Runs the specified tools in sequence for the given objective and action.

        Parameters:
            objective (str): The objective for running the tools.
            action (Dict): The action containing the tools to run.
            action_info_order (Optional[List[str]]): The order of action information to include in the Agent prompt.
            tool_info_order (Optional[List[str]]): The order of tool information to include in the Agent prompt.

        Returns:
            Optional[Dict]: The final result of the tool execution or an error dictionary.

        Raises:
            Exception: If an error occurs while running the tools in sequence.
        """
        results: Dict = {}
        tool_context: str = ""

        try:
            tools = self.get_tools_in_action(action=action)

            # Check if an error occurred
            if isinstance(tools, dict) and "error" in tools:
                return tools  # Stop execution and return the error message
            if not tools:
                return {"error": "No tools found for action"}

            tools_to_run = cast(List[Dict[str, Any]], tools)
            for tool in tools_to_run:
                payload = self.prime_tool_for_action(
                    objective=objective,
                    action=action,
                    tool=tool,
                    previous_results=results.get("data", None),
                    tool_context=tool_context,
                    action_info_order=action_info_order,
                    tool_info_order=tool_info_order,
                )

                if isinstance(payload, dict) and "error" in payload:
                    return payload  # Stop execution and return the error message

                tool_context = payload["thoughts"].get("next_tool_context")
                results = self.tool_utils.dynamic_tool(tool, payload)

                # Check if an error occurred
                if isinstance(results, dict) and results["status"] != "success":
                    return results  # Stop loop and return the error message

            return results

        except Exception as e:
            error_message = f"Error running tools in sequence: {e}"
            self.logger.log(error_message, "error")
            return {"error": error_message, "traceback": traceback.format_exc()}

    # --------------------------------------------------------------------------------------------------------
    # ------------------------------------------ Solution Example --------------------------------------------
    # --------------------------------------------------------------------------------------------------------

    def auto_execute(
        self, objective: str, context: str | None = None, threshold: float | None = 0.8
    ) -> Union[Dict, str, None]:
        """
        Automatically executes the actions for the given objective and context.

        Parameters:
            objective (str): The objective for the execution.
            context (Optional[str]): The context for the execution.
            threshold (Optional[float]): The threshold for action relevance (Lower is stricter). Default is 0.8.

        Returns:
            Union[Dict, str, None]: The result of the execution or an error dictionary.

        Raises:
            Exception: If an error occurs during execution.
        """
        try:
            action_list = self.get_relevant_items_for_objective(
                collection_name="Actions", objective=objective, threshold=threshold, num_results=10
            )
            if action_list:
                self.logger.log(f"\nSelecting Action for Objective:\n{objective}", "info", "Actions")
                order = ["Name", "Description"]
                available_actions = self.tool_utils.format_item_list(action_list, order)
                selected_action = self.select_action_for_objective(
                    objective=objective, action_list=available_actions or "", context=context
                )
                if not isinstance(selected_action, dict) or "action" not in selected_action:
                    return {"error": "Error Selecting Action"}
                selected_action = self.actions[selected_action["action"]]
                self.logger.log(f"\nSelected Action:\n{selected_action}", "info", "Actions")
            else:
                self.logger.log(f"\nCrafting Action for Objective:\n{objective}", "info", "Actions")
                order = ["Name", "Description", "Args"]
                threshold = 1
                tool_list = self.get_relevant_items_for_objective(
                    collection_name="Tools", objective=objective, threshold=threshold, num_results=10
                )
                available_tools = self.tool_utils.format_item_list(tool_list, order)
                selected_action = self.craft_action_for_objective(
                    objective=objective, tool_list=available_tools or "", context=context
                )
                self.logger.log(f"\nCrafted Action:\n{selected_action}", "info", "Actions")

                if isinstance(selected_action, dict) and "error" in selected_action:
                    return selected_action
                if not isinstance(selected_action, dict):
                    return {"error": "Error Creating Action"}

            action_info_order = ["Name", "Description"]
            tool_info_order = ["Name", "Description", "Args", "Instruction", "Example"]
            result = self.run_tools_in_sequence(
                objective=objective,
                action=selected_action,
                action_info_order=action_info_order,
                tool_info_order=tool_info_order,
            )
            # Check if an error occurred
            if result is None:
                return None
            if isinstance(result, dict) and result["status"] != "success":
                self.logger.log(f"\nAction Failed:\n{result['message']}", "error", "Actions")
                return result  # Stop execution and return the error message

            self.logger.log(f"\nAction Result:\n{result['data']}", "info", "Actions")
            return result
        except Exception as e:
            error_message = f"Error in running action: {e}"
            self.logger.log(error_message, "error", "Actions")
            return {"error": error_message, "traceback": traceback.format_exc()}
