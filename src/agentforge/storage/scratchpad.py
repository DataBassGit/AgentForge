import re
from typing import Optional, Union, List, Any

from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.utils.prompt_processor import PromptProcessor
from agentforge.agent import Agent
from agentforge.storage.memory import Memory


class ScratchPad(Memory):
    """
    ScratchPad memory storage that inherits from the base Memory class.
    Provides functionality for storing, retrieving, and updating user scratchpads.
    
    This class maintains two collections:
    1. The main scratchpad which contains the current summarized knowledge
    2. A log collection that stores individual entries before they're consolidated
    """

    def __init__(self, cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None):
        """
        Initialize the ScratchPad memory.
        
        Args:
            cog_name (str): Name of the cog to which this memory belongs.
            persona (Optional[str]): Optional persona name for further partitioning.
            collection_id (Optional[str]): Identifier for the main scratchpad collection.
        """
        super().__init__(cog_name, persona, collection_id)
        self.logger = Logger('Memory')
        self.parser = ParsingProcessor()
        self.prompt_processor = PromptProcessor()
        
        # Define the log collection name based on the main collection
        self.log_collection_name = f"scratchpad_log_{self.collection_name}"
        self.log_collection_name = self.parser.format_string(self.log_collection_name)

    def query_memory(self, query_keys: Optional[List[str]], _ctx: dict, _state: dict, num_results: int = 5) -> dict[str, Any]:
        """
        Query memory storage for relevant entries based on provided context and state.

        Args:
            query_keys (Optional[List[str]]): Keys to construct the query from context/state.
            _ctx (dict): External context data.
            _state (dict): Internal state data.
            num_results (int): Number of results to retrieve.
        """
        # For scratchpads, we don't use semantic search but instead just retrieve the content
        result = self.storage.load_collection(collection_name=self.collection_name)
        self.logger.debug(f"Retrieved scratchpad: {result}")
        
        if result and result.get('documents') and len(result['documents']) > 0:
            self.store.update({"readable": result.get('documents')})
            self.logger.debug(f"Query returned {len(result.get('ids', []))} results.")
            return
        
        # Return default message if no scratchpad exists
        default_msg = "No information available yet. This scratchpad will be updated as we learn more about the user."
        self.store.update({"readable": default_msg})


    def update_memory(self, update_keys: Optional[List[str]], _ctx: dict, _state: dict,
                      ids: Optional[Union[str, list[str]]] = None,
                      metadata: Optional[list[dict]] = None) -> None:
        """
        Update memory with new data using update_keys to extract from context/state.

        Args:
            update_keys (Optional[List[str]]): Keys to extract for update, or None to use all data.
            _ctx (dict): External context data.
            _state (dict): Internal state data.
            ids (Union[str, list[str]], optional): The IDs for the documents.
            metadata (list[dict], optional): Custom metadata for the documents (overrides generated metadata).
        """

        content = self.prompt_processor.value_to_markdown(val=_ctx)
        state = self.prompt_processor.value_to_markdown(val=_state)
        
        if not content:
            self.logger.warning("No content provided for scratchpad update")
            return
            
        # Save to the log collection
        self._save_scratchpad_log(content)
        self._save_scratchpad_log(state)
        
        # Check if it's time to consolidate the log
        self.check_scratchpad()

    def _save_scratchpad_log(self, content: str) -> None:
        """
        Save an entry to the scratchpad log.
        
        Args:
            content (str): The content to save in the log.
        """
        collection_size = self.storage.count_collection(self.log_collection_name)
        memory_id = [str(collection_size + 1)]
        
        self.logger.debug(
            f"Saving to Scratchpad Log: {self.log_collection_name}\nContent: {content}\nID: {memory_id}", 
        )
        
        self.storage.save_to_storage(
            collection_name=self.log_collection_name,
            data=[content],
            ids=memory_id,
            metadata=[{}]  # No special metadata needed for log entries
        )

    def _save_main_scratchpad(self, content: str) -> None:
        """
        Save or update the main scratchpad.
        
        Args:
            content (str): The content to save in the scratchpad.
        """
        self.logger.debug(
            f"Updating main scratchpad: {self.collection_name}\nContent: {content[:100]}...", 
        )
        
        self.storage.save_to_storage(
            collection_name=self.collection_name,
            data=[content],
            ids=["1"],  # Always use ID "1" to ensure we replace the existing entry
            metadata=[{}]  # No special metadata needed for main scratchpad
        )

    def _get_scratchpad_log(self) -> list:
        """
        Retrieve the scratchpad log entries.
        
        Returns:
            list: The scratchpad log entries as a list or an empty list if not found.
        """
        result = self.storage.load_collection(collection_name=self.log_collection_name)
        self.logger.debug(f"Scratchpad Log: {result}")
        
        if result and result.get('documents'):
            return result['documents']
        return []

    def check_scratchpad(self) -> Optional[str]:
        """
        Check if it's time to update the scratchpad based on the log entries.
        If there are enough log entries, consolidate them into the main scratchpad.
        
        Returns:
            Optional[str]: Updated scratchpad content if updated, None otherwise.
        """
        scratchpad_log = self._get_scratchpad_log()
        log_count = len(scratchpad_log)
        
        self.logger.debug(f"Checking scratchpad log. Number of entries: {log_count}")
        
        # If we have enough log entries, consolidate them
        if log_count >= 20:
            self.logger.debug(f"Scratchpad log count >= 20, updating scratchpad")
            
            # Create an agent to summarize the log
            scratchpad_agent = Agent(agent_name="scratchpad_agent")
            
            # Get the current scratchpad content
            current_scratchpad = self.store.get('readable', '')
            
            # Join all log entries
            scratchpad_log_content = "\n".join(scratchpad_log)
            
            # Run the agent to generate a new scratchpad
            agent_vars = {
                "scratchpad_log": scratchpad_log_content,
                "scratchpad": current_scratchpad
            }
            scratchpad_result = scratchpad_agent.run(**agent_vars)
            
            # Extract the updated scratchpad from the agent's response
            updated_scratchpad = self._extract_updated_scratchpad(scratchpad_result)
            
            # Save the updated scratchpad
            self._save_main_scratchpad(updated_scratchpad)
            
            # Clear the log after processing
            self.storage.delete_collection(self.log_collection_name)
            self.logger.debug(f"Cleared scratchpad log")
            
            return updated_scratchpad
            
        return None

    def _extract_updated_scratchpad(self, scratchpad_result: str) -> str:
        """
        Extract the updated scratchpad content from the ScratchpadAgent's output.
        
        Parameters:
            scratchpad_result (str): The full output from the ScratchpadAgent.
            
        Returns:
            str: The extracted updated scratchpad content.
        """
        pattern = r'<updated_scratchpad>(.*?)</updated_scratchpad>'
        match = re.search(pattern, scratchpad_result, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        else:
            self.logger.warning("No updated scratchpad content found in the result.")
            return "No updated scratchpad content could be extracted."

    def delete(self, ids: Union[str, list[str]] = None) -> None:
        """
        Delete the scratchpad and its log.
        
        Args:
            ids (Union[str, list[str]], optional): Not used for scratchpads.
        """
        # Delete both the main scratchpad and the log
        self.storage.delete_collection(self.collection_name)
        self.storage.delete_collection(self.log_collection_name)
        self.logger.debug(f"Deleted scratchpad and log collections") 