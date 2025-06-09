"""
PersonaMemory implementation for AgentForge.

This module provides a specialized memory system for managing persona-related facts
and narratives, integrating with specialized agents for retrieval, narrative generation,
and updates.
"""

from typing import Optional, Dict, Any, List, Union, Tuple
from agentforge.storage.memory import Memory
from agentforge.agent import Agent
from agentforge.utils.logger import Logger
from agentforge.utils.prompt_processor import PromptProcessor

# -----------------------------------------------------------------
# Public Interface
# -----------------------------------------------------------------
class PersonaMemory(Memory):
    """
    Specialized memory for managing persona-related facts and narratives.
    Integrates with retrieval, narrative, and update agents for dynamic persona management.
    """
    def __init__(self, cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None):
        """
        Initialize PersonaMemory with specialized agents for persona management.
        Args:
            cog_name (str): Name of the cog to which this memory belongs.
            persona (Optional[str]): Optional persona name for further partitioning.
            collection_id (Optional[str]): Identifier for the collection.
        """
        super().__init__(cog_name, persona, collection_id, logger_name="PersonaMemory")
        self.prompt_processor = PromptProcessor()
        self._initialize_agents()
        self.narrative: Optional[str] = None

    def _initialize_agents(self) -> None:
        """
        Initialize the specialized agents used by PersonaMemory.
        """
        try:
            self.retrieval_agent = Agent(agent_name="persona_retrieval_agent")
            self.narrative_agent = Agent(agent_name="persona_narrative_agent")
            self.update_agent = Agent(agent_name="persona_update_agent")
            self.logger.debug("Initialized persona memory agents")
        except Exception as e:
            self.logger.error(f"Failed to initialize persona agents: {e}")
            raise

    def _build_collection_name(self) -> None:
        """
        Build a collection name specific to persona memory.
        Sets self.collection_name to 'persona_facts_{persona|cog_name}'.
        """
        base_name = self.collection_id or "persona_facts"
        storage_suffix = self._resolve_storage_id()
        self.collection_name = f"{base_name}_{storage_suffix}"

    # -----------------------------------------------------------------
    # Context Preparation and Fact Retrieval
    # -----------------------------------------------------------------
    def _load_context(self, keys: Optional[List[str]], _ctx: dict, _state: dict, num_results: int) -> Tuple[str, List[str]]:
        static_persona = self._get_static_persona_markdown()
        query_keys = self._extract_query_keys(keys, _ctx, _state)
        initial_facts = self._retrieve_initial_facts(query_keys, num_results)
        return static_persona, initial_facts

    def _extract_query_keys(self, keys: Optional[List[str]], _ctx: dict, _state: dict) -> List[str]:
        """
        Extract query keys from context and state.
        Args:
            keys: Keys to extract.
            _ctx: External context data.
            _state: Internal state data.
        Returns:
            List of extracted query keys.
        """
        if not keys:
            return []
        try:
            extracted = self._extract_keys(keys, _ctx, _state)
            if isinstance(extracted, dict):
                return list(extracted.values())
            if isinstance(extracted, list):
                return extracted
            return [str(extracted)]
        except Exception as e:
            self.logger.warning(f"Failed to extract query keys: {e}")
            return []

    def _retrieve_initial_facts(self, query_keys: List[str], num_results: int) -> List[str]:
        """
        Perform initial storage lookup for persona facts.
        Args:
            query_keys: List of query keys.
            num_results: Number of results to retrieve.
        Returns:
            List of retrieved facts.
        """
        if not query_keys:
            return []
        results = self.storage.query_storage(
            collection_name=self.collection_name,
            query=query_keys,
            num_results=num_results
        )
        return results.get('documents', [])

    # -----------------------------------------------------------------
    # Semantic Retrieval
    # -----------------------------------------------------------------
    def _retrieve_semantic_facts(self, _ctx: dict, _state: dict, static_persona: str, initial_facts: List[str], num_results: int) -> List[str]:
        queries = self._generate_semantic_queries(_ctx, _state, static_persona, initial_facts, num_results)
        semantic_facts = self._perform_semantic_search(queries, num_results)
        return self._deduplicate_facts(initial_facts + semantic_facts)

    def _generate_semantic_queries(self, _ctx: dict, _state: dict, static_persona: str, retrieved_facts: List[str], num_results: int) -> List[str]:
        retrieval_response = self.retrieval_agent.run(
            _ctx=_ctx,
            _state=_state,
            persona_static=static_persona,
            retrieved_facts=retrieved_facts,
            num_results=num_results
        )
        if not isinstance(retrieval_response, dict) or 'queries' not in retrieval_response:
            self.logger.warning("Retrieval agent returned invalid response format")
            return []
        queries = retrieval_response.get('queries', [])
        if not queries:
            self.logger.warning("No queries generated by retrieval agent")
        return queries

    def _perform_semantic_search(self, queries: List[str], num_results: int) -> List[str]:
        """
        Perform semantic search using generated queries.
        Args:
            queries: List of queries.
            num_results: Number of results to retrieve.
        Returns:
            List of found facts.
        """
        if not queries:
            return []
        results = self.storage.query_storage(
            collection_name=self.collection_name,
            query=queries,
            num_results=num_results
        )
        return results.get('documents', [])

    def _deduplicate_facts(self, facts: List[str]) -> List[str]:
        """
        Deduplicate facts while preserving order.
        Args:
            facts: List of facts.
        Returns:
            List of unique facts.
        """
        unique_facts = []
        seen = set()
        for fact in facts:
            if fact not in seen:
                seen.add(fact)
                unique_facts.append(fact)
        return unique_facts

    # -----------------------------------------------------------------
    # Narrative Generation
    # -----------------------------------------------------------------
    def _generate_narrative(self, _ctx: dict, _state: dict, static_persona: str, facts: List[str]) -> str:
        narrative_response = self.narrative_agent.run(
            _ctx=_ctx,
            _state=_state,
            persona_static=static_persona,
            retrieved_facts=facts
        )
        if narrative_response and 'narrative' in narrative_response:
            return narrative_response['narrative']
        return self._generate_static_only_narrative(static_persona)

    def _generate_static_only_narrative(self, static_persona: str) -> str:
        """
        Generate a narrative using only static persona when no dynamic facts are available.
        Updates self.store with the static narrative instead of returning data.
        
        Args:
            static_persona: The static persona information.
        Returns:
            The static narrative.
        """
        return f"Based on the static persona information: {static_persona}"

    def _get_static_persona_markdown(self) -> str:
        """
        Get the static persona information formatted as markdown.
        Returns:
            Markdown formatted static persona data.
        """
        from agentforge.config import Config
        config = Config()
        cog_config = None
        if hasattr(self, 'cog_name') and self.cog_name:
            try:
                cog_data = config.load_cog_data(self.cog_name)
                cog_config = cog_data.get('cog', {}) if cog_data else None
            except Exception:
                pass
        persona_data = config.resolve_persona(cog_config=cog_config, agent_config=None)
        if not persona_data or 'static' not in persona_data:
            return "No static persona information available."
        static_content = persona_data.get('static', {})
        persona_settings = config.settings.system.persona
        persona_md = self.prompt_processor.build_persona_markdown(static_content, persona_settings)
        return persona_md or "No static persona information available."

    # -----------------------------------------------------------------
    # Memory Updating
    # -----------------------------------------------------------------
    def _determine_update_action(self, _ctx: dict, _state: dict, static_persona: str, facts: List[str]) -> Tuple[str, List[dict]]:
        update_response = self.update_agent.run(
            _ctx=_ctx,
            _state=_state,
            persona_static=static_persona,
            retrieved_facts=facts
        )
        if update_response and 'action' in update_response:
            return update_response['action'], update_response.get('new_facts', [])
        return 'none', []

    def _apply_update_action(self, action: str, new_facts: List[dict]) -> None:
        for fact_data in new_facts:
            if not isinstance(fact_data, dict) or 'fact' not in fact_data:
                self.logger.warning("Invalid fact format in update response")
                continue
            new_fact = fact_data.get('fact')
            supersedes = fact_data.get('supersedes', [])
            if not new_fact:
                self.logger.warning("Empty fact provided")
                continue
            if action == 'add':
                if self._is_duplicate_fact(new_fact):
                    self.logger.debug(f"Skipping duplicate fact: {new_fact}")
                    continue
                self.logger.info(f"Adding new persona fact: {new_fact}")
                fact_metadata_list = [{
                    'type': 'persona_fact',
                    'source': 'update_agent',
                    'superseded': False
                }]
                self.storage.save_to_storage(
                    collection_name=self.collection_name,
                    data=[new_fact],
                    metadata=fact_metadata_list
                )
            elif action == 'update':
                self.logger.info(f"Updating persona with new fact: {new_fact}")
                fact_metadata_list = [{
                    'type': 'persona_fact',
                    'source': 'update_agent',
                    'superseded': False,
                    'supersedes': ','.join(supersedes) if supersedes else ''
                }]
                self.storage.save_to_storage(
                    collection_name=self.collection_name,
                    data=[new_fact],
                    metadata=fact_metadata_list
                )
                self.logger.debug(f"Marked facts as superseded: {supersedes}")

    def _is_duplicate_fact(self, new_fact: str) -> bool:
        """
        Check if an exact duplicate of the new fact already exists in storage.
        Args:
            new_fact (str): The fact to check for duplicates.
        Returns:
            bool: True if an exact duplicate exists, False otherwise.
        """
        try:
            results = self.storage.query_storage(
                collection_name=self.collection_name,
                query=new_fact,
                num_results=10
            )
            if not results or not results.get('documents'):
                return False
            for document in results['documents']:
                if document.strip() == new_fact.strip():
                    return True
            return False
        except Exception as e:
            self.logger.warning(f"Error checking for duplicate facts: {e}")
            return False

    # -----------------------------------------------------------------
    # Public Interface
    # -----------------------------------------------------------------
    
    def query_memory(self, query_keys: Optional[List[str]], _ctx: dict, _state: dict, num_results: int = 5) -> None:
        """
        Query persona memory using retrieval and narrative agents.
        Updates self.store with narrative and retrieved facts instead of returning data.
        
        Args:
            query_keys: Keys to extract from context/state, or None to use all data.
            _ctx: External context data.
            _state: Internal state data.
            num_results: Number of results to retrieve per query.
        """
        try:
            static_persona, initial_facts = self._load_context(query_keys, _ctx, _state, num_results)
            semantic_facts = self._retrieve_semantic_facts(_ctx, _state, static_persona, initial_facts, num_results)
            narrative = self._generate_narrative(_ctx, _state, static_persona, semantic_facts)
            self.narrative = narrative
            self.store = {
                '_narrative': narrative,
                '_static': static_persona,
                '_retrieved_facts': semantic_facts,
                'raw_facts': semantic_facts
            }
            self.logger.debug(f"Successfully generated narrative and stored {len(semantic_facts)} facts")
        except Exception as e:
            self.logger.error(f"Error in query_memory: {e}")
            raise Exception(f"Error in query_memory: {e}")

    def update_memory(self, update_keys: Optional[List[str]], _ctx: dict, _state: dict,
                     ids: Optional[Union[str, List[str]]] = None,
                     metadata: Optional[List[dict]] = None,
                     num_results: int = 5) -> None:
        """
        Update persona memory using retrieval and update agents.
        Args:
            update_keys: Keys to extract from context/state, or None to use all data.
            _ctx: External context data.
            _state: Internal state data.
            ids: Ignored; IDs are auto-generated for persona facts.
            metadata: Ignored; custom metadata is generated for persona facts.
            num_results: Number of results to retrieve per query.
        """
        try:
            static_persona, initial_facts = self._load_context(update_keys, _ctx, _state, num_results)
            semantic_facts = self._retrieve_semantic_facts(_ctx, _state, static_persona, initial_facts, num_results)
            action, new_facts = self._determine_update_action(_ctx, _state, static_persona, semantic_facts)
            if action != 'none':
                self._apply_update_action(action, new_facts)
        except Exception as e:
            self.logger.error(f"Error in update_memory: {e}")
            raise Exception(f"Error in update_memory: {e}")

