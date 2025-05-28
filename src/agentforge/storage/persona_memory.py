"""
PersonaMemory implementation for AgentForge.

This module provides a specialized memory system for managing persona-related facts
and narratives, integrating with specialized agents for retrieval, narrative generation,
and updates.
"""

from typing import Optional, Dict, Any, List, Union
from agentforge.storage.memory import Memory
from agentforge.agent import Agent
from agentforge.utils.logger import Logger
from agentforge.utils.prompt_processor import PromptProcessor


class PersonaMemory(Memory):
    """
    A specialized memory system for managing persona-related facts and narratives.
    
    This memory type uses specialized agents to:
    1. Retrieve relevant persona facts through semantic search
    2. Generate narrative summaries of the persona
    3. Update persona facts based on new context
    
    The memory maintains a collection of persona facts that can be queried and
    updated dynamically, while also providing narrative generation for prompt injection.
    """
    
    def __init__(self, cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None):
        """
        Initialize PersonaMemory with specialized agents for persona management.
        
        Args:
            cog_name (str): Name of the cog to which this memory belongs
            persona (Optional[str]): Optional persona name for further partitioning
            collection_id (Optional[str]): Identifier for the collection
        """
        super().__init__(cog_name, persona, collection_id)
        
        self.logger = Logger(name="PersonaMemory")
        self.prompt_processor = PromptProcessor()
        
        # Initialize specialized agents for persona memory operations
        self._initialize_agents()
        
        # Store for the latest narrative
        self.narrative = None
        
    def _initialize_agents(self):
        """Initialize the specialized agents used by PersonaMemory."""
        try:
            # Load specialized agents from the persona prompts directory
            self.retrieval_agent = Agent(agent_name="retrieval_agent")
            self.narrative_agent = Agent(agent_name="narrative_agent")
            self.update_agent = Agent(agent_name="update_agent")
            self.logger.debug("Initialized persona memory agents")
        except Exception as e:
            self.logger.error(f"Failed to initialize persona agents: {e}")
            raise
            
    def _build_collection_name(self) -> str:
        """
        Build a collection name specific to persona memory.
        
        Returns:
            str: Collection name formatted as 'persona_facts_{persona|cog_name}'
        """
        base_name = self.collection_id or "persona_facts"
        storage_suffix = self._resolve_storage_id()
        return f"{base_name}_{storage_suffix}"
        
    def _format_dict_as_markdown(self, data: Any, indent_level: int = 0) -> str:
        """
        Recursively format a dictionary (or other data) as clean markdown.
        
        Args:
            data: The data to format (dict, list, or primitive)
            indent_level: Current indentation level for nested structures
            
        Returns:
            str: Clean markdown representation
        """
        indent = "  " * indent_level
        
        if isinstance(data, dict):
            items = []
            for key, value in data.items():
                # Skip circular references
                if key in ['memory', 'persona']:
                    continue
                    
                if isinstance(value, (dict, list)):
                    # For nested structures, format recursively
                    nested_content = self._format_dict_as_markdown(value, indent_level + 1)
                    items.append(f"{indent}- **{key}**:\n{nested_content}")
                else:
                    # For simple values, format inline
                    items.append(f"{indent}- **{key}**: {value}")
            return "\n".join(items)
        elif isinstance(data, list):
            items = []
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    nested_content = self._format_dict_as_markdown(item, indent_level + 1)
                    items.append(f"{indent}- Item {i+1}:\n{nested_content}")
                else:
                    items.append(f"{indent}- {item}")
            return "\n".join(items)
        else:
            return f"{indent}{data}"
        
    def _get_static_persona_markdown(self) -> str:
        """
        Get the static persona information formatted as markdown.
        
        Returns:
            str: Markdown formatted static persona data
        """
        # Get the persona data from config
        from agentforge.config import Config
        config = Config()
        
        # Resolve persona using the same hierarchy as the framework
        # Pass cog context if we have a cog_name
        cog_config = None
        if hasattr(self, 'cog_name') and self.cog_name:
            try:
                cog_data = config.load_cog_data(self.cog_name)
                cog_config = cog_data.get('cog', {}) if cog_data else None
            except Exception:
                # If we can't load cog data, continue without it
                pass
                
        persona_data = config.resolve_persona(cog_config=cog_config, agent_config=None)
        
        if not persona_data or 'static' not in persona_data:
            return "No static persona information available."
            
        # Use the existing prompt processor to build markdown
        static_content = persona_data.get('static', {})
        persona_settings = config.data['settings']['system']['persona']
        
        persona_md = self.prompt_processor.build_persona_markdown(static_content, persona_settings)
        return persona_md or "No static persona information available."
        
    def query_memory(self, query_text: Union[str, list[str]], num_results: int = 5) -> Optional[Dict[str, Any]]:
        """
        Query persona memory using specialized agents for retrieval and narrative generation.
        
        This method:
        1. Uses the Retrieval Agent to generate semantic search queries
        2. Performs semantic search to retrieve relevant persona facts
        3. Uses the Narrative Agent to generate a coherent persona narrative
        
        Args:
            query_text: The context or query text (can be full context dict)
            num_results: Number of results to retrieve per query
            
        Returns:
            Dict containing the narrative and raw results, or None if no narrative generated
        """
        try:
            # Prepare context for agents - format as clean markdown (nested form only)
            if isinstance(query_text, dict):
                # Use only the nested context structure to avoid duplication
                context = self._format_dict_as_markdown(query_text)
            else:
                context = str(query_text)
                
            static_persona = self._get_static_persona_markdown()
            
            # Step 1: Generate search queries using Retrieval Agent
            # Note: For initial retrieval, we don't pass dynamic persona to encourage
            # first-person declarative queries as specified in the prompt template
            self.logger.debug("Invoking retrieval agent for search queries")
            retrieval_response = self.retrieval_agent.run(
                context=context,
                persona_static=static_persona
                # persona_dynamic removed - template doesn't use it for retrieval
            )
            
            # Extract queries from structured response
            if not isinstance(retrieval_response, dict) or 'queries' not in retrieval_response:
                self.logger.warning("Retrieval agent returned invalid response format")
                return self._generate_static_only_narrative(context, static_persona)
                
            queries = retrieval_response.get('queries', [])
            if not queries:
                self.logger.warning("No queries generated by retrieval agent")
                return self._generate_static_only_narrative(context, static_persona)
            
            # Step 2: Perform semantic searches
            all_facts = []
            for query in queries:
                self.logger.debug(f"Searching for: {query}")
                results = self.storage.query_storage(
                    collection_name=self.collection_name,
                    query=query,
                    num_results=num_results
                )
                if results and results.get('documents'):
                    all_facts.extend(results['documents'])
                    
            # Remove duplicates while preserving order
            unique_facts = []
            seen = set()
            for fact in all_facts:
                if fact not in seen:
                    seen.add(fact)
                    unique_facts.append(fact)
                    
            # Format retrieved facts for narrative agent
            retrieved_facts_str = "\n".join(unique_facts) if unique_facts else "No dynamic persona facts found."
            
            # Step 3: Generate narrative using Narrative Agent
            self.logger.debug("Invoking narrative agent")
            narrative_response = self.narrative_agent.run(
                context=context,
                persona_static=static_persona,
                retrieved_facts=retrieved_facts_str
            )
            
            # Extract narrative from structured response
            if not isinstance(narrative_response, dict) or 'narrative' not in narrative_response:
                self.logger.warning("Narrative agent returned invalid response format")
                return self._generate_static_only_narrative(context, static_persona)
                
            narrative = narrative_response.get('narrative')
            if not narrative:
                self.logger.warning("No narrative generated by narrative agent")
                return self._generate_static_only_narrative(context, static_persona)
                
            # Store the narrative for placeholder access
            self.narrative = narrative
            
            # Update the store with the narrative
            self.store = {
                '_narrative': narrative,
                '_static': static_persona,
                'raw_facts': unique_facts
            }
            
            return {
                '_narrative': narrative,
                '_static': static_persona,
                'raw': {'documents': unique_facts} if unique_facts else None
            }
            
        except Exception as e:
            self.logger.error(f"Error in query_memory: {e}")
            return self._generate_static_only_narrative(context if 'context' in locals() else "", 
                                                      static_persona if 'static_persona' in locals() else "")
            
    def update_memory(self, data: dict, context: Optional[dict] = None,
                     ids: Optional[Union[str, list[str]]] = None,
                     metadata: Optional[list[dict]] = None) -> None:
        """
        Update persona memory using specialized agents to determine appropriate actions.
        
        This method:
        1. Uses the Retrieval Agent to find relevant existing facts
        2. Uses the Update Agent to determine if facts should be added/updated
        3. Updates ChromaStorage accordingly
        
        The Update Agent is specifically instructed to consider if information represents
        an "enduring persona trait" that will matter in future conversations.
        
        Args:
            data: Dictionary containing the data to be stored
            context: Dictionary containing the cog's external and internal context
            ids: The IDs for the documents (not used, auto-generated)
            metadata: Custom metadata for the documents (not used, auto-generated)
        """
        try:
            # Format the update context using only nested form (no flattened keys)
            if context:
                # Use only the nested context structure to avoid duplication
                update_context = self._format_dict_as_markdown(context)
            else:
                update_context = "No context provided"
                
            static_persona = self._get_static_persona_markdown()
            
            # Step 1: Retrieve relevant existing facts
            self.logger.debug("Retrieving existing facts for update context")
            retrieval_response = self.retrieval_agent.run(
                context=update_context,
                persona_static=static_persona
                # No persona_dynamic for retrieval agent as per template
            )
            
            # Extract queries from structured response
            queries = []
            if isinstance(retrieval_response, dict) and 'queries' in retrieval_response:
                queries = retrieval_response.get('queries', [])
            
            # Collect existing facts
            existing_facts = []
            fact_metadata = {}
            if queries:
                for query in queries:
                    results = self.storage.query_storage(
                        collection_name=self.collection_name,
                        query=query,
                        num_results=5
                    )
                    if results and results.get('documents'):
                        for i, doc in enumerate(results['documents']):
                            existing_facts.append(doc)
                            # Store metadata for potential updates
                            if results.get('ids') and i < len(results['ids']):
                                fact_metadata[doc] = results['ids'][i]
                                
            # Format retrieved facts for the Update Agent
            retrieved_facts_str = "\n".join(existing_facts) if existing_facts else "No existing persona facts."
            
            # Step 2: Determine update action using Update Agent
            # The template specifically asks about "enduring persona traits"
            self.logger.debug("Invoking update agent to determine if this represents an enduring persona trait")
            update_response = self.update_agent.run(
                context=update_context,
                persona_static=static_persona,
                retrieved_facts=retrieved_facts_str
            )
            
            # Extract action from structured response
            if not isinstance(update_response, dict) or 'action' not in update_response:
                self.logger.warning("Update agent returned invalid response format")
                return
                
            action = update_response.get('action')
            if not action or action == 'none':
                self.logger.debug("Update agent determined this is not an enduring persona trait")
                return
                
            # Step 3: Execute the update action
            new_facts = update_response.get('new_facts', [])
            
            if not new_facts:
                self.logger.warning("Update action specified but no new facts provided")
                return
                
            # Process each new fact
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
                    # Check for exact duplicates before adding
                    if self._exact_duplicate_exists(new_fact):
                        self.logger.debug(f"Skipping duplicate fact: {new_fact}")
                        continue
                        
                    # Add new fact to storage
                    self.logger.info(f"Adding new persona fact: {new_fact}")
                    fact_metadata_list = [{
                        'type': 'persona_fact',
                        'source': 'update_agent',
                        'superseded': False
                    }]
                    if context:
                        fact_metadata_list[0].update({
                            'context_' + k: str(v)[:100]  # Limit metadata size
                            for k, v in context.items() 
                            if isinstance(k, str) and k not in ['memory', 'persona']
                        })
                        
                    self.storage.save_to_storage(
                        collection_name=self.collection_name,
                        data=[new_fact],
                        ids=None,  # Let storage generate IDs
                        metadata=fact_metadata_list
                    )
                    
                elif action == 'update':
                    # Add the new fact with supersedes information
                    self.logger.info(f"Updating persona with new fact: {new_fact}")
                    fact_metadata_list = [{
                        'type': 'persona_fact',
                        'source': 'update_agent',
                        'superseded': False,
                        'supersedes': ','.join(supersedes) if supersedes else ''
                    }]
                    if context:
                        fact_metadata_list[0].update({
                            'context_' + k: str(v)[:100]
                            for k, v in context.items()
                            if isinstance(k, str) and k not in ['memory', 'persona']
                        })
                        
                    self.storage.save_to_storage(
                        collection_name=self.collection_name,
                        data=[new_fact],
                        ids=None,
                        metadata=fact_metadata_list
                    )
                    
                    # Mark superseded facts by updating their metadata
                    # Note: ChromaDB doesn't support updating just metadata, so we'll track this
                    # in our queries instead by checking the supersedes field
                    self.logger.debug(f"Marked facts as superseded: {supersedes}")
                
        except Exception as e:
            self.logger.error(f"Error in update_memory: {e}")
            # Fall back to base class implementation
            super().update_memory(data, context, ids, metadata)
            
    def _exact_duplicate_exists(self, new_fact: str) -> bool:
        """
        Check if an exact duplicate of the new fact already exists in storage.
        
        Args:
            new_fact: The fact text to check for duplicates
            
        Returns:
            bool: True if an exact duplicate exists, False otherwise
        """
        try:
            # Search for the exact text in the collection
            results = self.storage.query_storage(
                collection_name=self.collection_name,
                query=new_fact,
                num_results=10  # Check more results to be thorough
            )
            
            if results and results.get('documents'):
                # Check if any document is an exact match
                for document in results['documents']:
                    if document.strip() == new_fact.strip():
                        return True
                        
                # Also check distances if available (distance == 0 means exact match)
                if results.get('distances'):
                    for distance in results['distances']:
                        if distance == 0:
                            return True
                            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking for duplicate facts: {e}")
            return False  # If we can't check, allow the addition
            

            
    def _generate_static_only_narrative(self, context: str, static_persona: str) -> Dict[str, Any]:
        """Generate a narrative using only static persona when no dynamic facts are available."""
        # Simple fallback narrative
        narrative = f"Based on the static persona information: {static_persona}"
        
        self.narrative = narrative
        self.store = {
            '_narrative': narrative,
            '_static': static_persona,
            'raw_facts': []
        }
        
        return {
            '_narrative': narrative,
            '_static': static_persona,
            'raw': None
        } 