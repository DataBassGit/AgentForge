# src/agentforge/cog.py

import importlib
from typing import Optional, Dict, Any
from agentforge.config import Config
from agentforge.agent import Agent  # assuming a base Agent exists


class Cog:
    """
    A Cognitive Architecture (Cog) engine that orchestrates multiple agents
    defined in a YAML configuration.
    """

    def __init__(self, cog_name: str, enable_trail_logging: bool = True):
        """
        Initializes the Cog engine.

        Args:
            cog_name (str): The name of the cog (YAML file name without extension).
            enable_trail_logging (bool): Whether to record the global context after each node execution.
        """
        self.cog_name: str = cog_name if cog_name is not None else self.__class__.__name__
        self.thought_flow_trail = [] if enable_trail_logging else None
        self.global_context: Dict[str, Any] = {}
        self.config = Config()
        self._load_flow_data()
        self._build_nodes()

    def _load_flow_data(self) -> None:
        """
        Loads the cog (flow) configuration from the config system.
        """
        self.cog = self.config.load_cog_data(self.cog_name).copy()

    def _build_nodes(self) -> None:
        """
        Builds a dictionary of node (agent) instances from the agents list in the YAML.

        Each agent definition may specify:
          - id (required)
          - type (optional): If missing, defaults to the base Agent.
             If provided, it must be a fully qualified import path like 'my_agents.test_agent.TestAgent'.
          - template_file (optional): Can be used by the agent for prompt loading.
        """
        nodes = {}
        agents_list = self.cog.get('agents', [])
        for agent_def in agents_list:
            agent_id = agent_def.get('id')
            if not agent_id:
                continue  # skip agents without an id

            # If 'type' is not provided, default to Agent.
            if 'type' not in agent_def:
                agent_class = Agent
            else:
                agent_class_name = agent_def['type']
                # The provided type must contain a dot, e.g., "module.submodule.ClassName"
                if '.' not in agent_class_name:
                    raise ValueError(
                        f"Invalid agent type format for agent '{agent_id}': '{agent_class_name}'. "
                        "It must be a fully qualified import path (e.g., 'my_agents.test_agent.TestAgent')."
                    )
                try:
                    parts = agent_class_name.split('.')
                    module_path = '.'.join(parts[:-1])
                    class_name = parts[-1]
                    module = importlib.import_module(module_path)
                    agent_class = getattr(module, class_name)
                except Exception as e:
                    raise ImportError(
                        f"Could not import agent class for agent '{agent_id}' with type '{agent_class_name}': {e}"
                    )

            # Instantiate the agent using its id.
            nodes[agent_id] = agent_class(agent_id)
        self.nodes = nodes

    def get_next_node(self, current_node_id: str) -> Optional[str]:
        """
        Determines the next node ID based on the current node's transition and global context.

        Returns:
            The next node ID as a string, or None if the flow ends.
        """
        transitions = self.cog.get('flow', {}).get('transitions', {})
        node_transition = transitions.get(current_node_id)
        if node_transition is None:
            # No transition defined; end the flow.
            return None

        if isinstance(node_transition, dict):
            if node_transition.get("end", False):
                return None
            # If a "next" key exists, use that.
            if "next" in node_transition:
                return node_transition["next"]
            # Otherwise, assume that the first key that is not "end" is the decision key.
            decision_key = None
            for key in node_transition:
                if key not in ("end", "next"):
                    decision_key = key
                    break
            if decision_key:
                decision_map = node_transition[decision_key]
                decision_value = self.global_context.get(decision_key)
                if decision_value is not None and decision_value in decision_map:
                    return decision_map[decision_value]
                elif "default" in decision_map:
                    return decision_map["default"]
                else:
                    return None
            # Fallback if no decision key is found.
            return None
        else:
            # If not a dict, assume it is a simple string.
            return node_transition

    def execute(self) -> Optional[Dict[str, Any]]:
        """
        Executes the cog by iteratively running agents as defined in the flow.

        Returns:
            The final global context if execution completes successfully, or None if an agent fails.
        """
        current_node_id = self.cog.get('flow', {}).get('start')
        if not current_node_id:
            return None

        while True:
            agent = self.nodes.get(current_node_id)
            if agent is None:
                # If an agent is not found, halt execution.
                return None
            try:
                output = agent.run(**self.global_context)
            except Exception as e:
                # Agent failure: halt execution.
                return None

            if output:
                self.global_context.update(output)

            if self.thought_flow_trail is not None:
                self.thought_flow_trail.append(self.global_context.copy())

            next_node = self.get_next_node(current_node_id)
            if next_node is None:
                break
            current_node_id = next_node

        return self.global_context
