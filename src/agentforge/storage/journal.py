import os
from datetime import datetime
from typing import Optional, Union, Dict, Any, List

from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.agent import Agent
from agentforge.storage.memory import Memory
import agentforge.tools.semantic_chunk as chunker


class Journal(Memory):
    """
    Journal memory storage that inherits from the base Memory class.
    Provides functionality for storing, retrieving, and generating journal entries.
    
    This class maintains three collections:
    1. journal_log_table: Raw interaction logs that feed into journal creation
    2. whole_journal_entries: Complete journal entries
    3. journal_chunks_table: Semantic chunks of entries for efficient retrieval
    """

    def __init__(self, cog_name: str, persona: Optional[str] = None, collection_id: Optional[str] = None):
        """
        Initialize the Journal memory.
        
        Args:
            cog_name (str): Name of the cog to which this memory belongs.
            persona (Optional[str]): Optional persona name for further partitioning.
            collection_id (Optional[str]): Identifier for the collection (defaults to "journal").
        """
        # If no collection_id is provided, use "journal" as default
        if not collection_id:
            collection_id = "journal"
            
        super().__init__(cog_name, persona, collection_id)
        self.logger = Logger('Memory')
        self.parser = ParsingProcessor()
        
        # Define the collection names for different journal components
        self.log_collection_name = "journal_log_table"
        self.whole_entries_collection = "whole_journal_entries"
        self.chunks_collection = "journal_chunks_table"
        
        # Initialize journal agents
        self.journal_agent = Agent(agent_name="JournalAgent")
        self.journal_thought = Agent(agent_name="JournalThoughtAgent")
        
        # Initialize other properties
        self.results = ''
        self.filepath = ''
        self.thoughts = None
        
        # Default relevance threshold for retrieval
        self.relevance_threshold = 0.65
        
    def query_memory(self, query_text: Union[str, list[str]], num_results: int = 2) -> Optional[Dict[str, Any]]:
        """
        Query the journal memory based on the query text and categories.
        
        Args:
            query_text (Union[str, list[str]]): The text to search for, or a list where the first 
                                               item is the message and the second is categories.
            num_results (int): Number of results to return (defaults to 2).
            
        Returns:
            Optional[Dict[str, Any]]: The journal entries as a formatted string.
        """
        message = ""
        categories = ""
        
        # Extract message and categories if provided
        if isinstance(query_text, list) and len(query_text) >= 2:
            message = query_text[0]
            categories = query_text[1]
        elif isinstance(query_text, str):
            message = query_text
        
        # Format query with categories if available
        journal_query = message
        if categories:
            journal_query = f"{message}\n\n Related Categories: {categories}"
        
        self.logger.debug(f"Querying journal with: {journal_query}")
        
        # Query the chunk collection
        journal_chunks = self.storage.query_storage(
            collection_name=self.chunks_collection,
            query=journal_query,
            num_results=num_results
        )
        
        # Create a dictionary to store the recalled memories
        recalled_memories = {
            'ids': [],
            'metadatas': [],
            'documents': []
        }
        
        if journal_chunks:
            self.logger.debug(f"Found journal chunks: {journal_chunks}")
            
            if 'ids' in journal_chunks:
                # Handle single result (non-list response)
                source_id = journal_chunks.get('metadatas', {}).get('Source_ID')
                
                if source_id:
                    # Retrieve the full journal entry based on the source_id
                    filters = {"id": {"$eq": source_id}}
                    full_entry = self.storage.load_collection(
                        collection_name=self.whole_entries_collection,
                        where=filters
                    )
                    
                    if full_entry and full_entry.get('documents'):
                        recalled_memories['ids'].append(full_entry['ids'][0])
                        recalled_memories['metadatas'].append(
                            {key: value for key, value in full_entry['metadatas'][0].items() if
                             key.lower() not in ['source', 'isotimestamp', 'unixtimestamp']}
                        )
                        recalled_memories['documents'].append(full_entry['documents'][0])
        
        # Format the recalled memories
        formatted_entries = self._format_journal_entries(recalled_memories)
        
        # Store in Memory's store attribute
        self.store = {
            'entries': formatted_entries,
            'raw': recalled_memories
        }
        
        return self.store
        
    def update_memory(self, data: dict, context: Optional[dict] = None, 
                       ids: Optional[Union[str, list[str]]] = None,
                       metadata: Optional[list[dict]] = None) -> None:
        """
        Update journal memory by adding an entry to the journal log.
        If there are enough entries, it will trigger a journal creation.
        
        Args:
            data (dict): Dictionary containing the data to be stored.
            context (dict, optional): Dictionary containing the cog's external and internal context.
            ids (Union[str, list[str]], optional): The IDs for the documents (not used).
            metadata (list[dict], optional): Custom metadata for the documents.
        """
        # Extract content from the data and metadata from context
        message = None
        response = None
        meta_dict = {}
        
        # Try to extract message from different keys
        for key in ['message', 'content', 'text', 'query']:
            if key in data:
                message = data[key]
                break
                
        # Try to extract response from different keys
        for key in ['response', 'answer', 'reply']:
            if key in data:
                response = data[key]
                break
        
        # Get metadata from context if available
        if context:
            # Extract user information if available
            if 'external' in context and isinstance(context['external'], dict):
                for key in ['user', 'username', 'user_id']:
                    if key in context['external']:
                        meta_dict['User'] = context['external'][key]
                        break
            
            # Extract channel information if available
            for ctx_type in ['external', 'internal']:
                if ctx_type in context and isinstance(context[ctx_type], dict):
                    for key in ['channel', 'source', 'platform']:
                        if key in context[ctx_type]:
                            meta_dict['channel'] = context[ctx_type][key]
                            break
        
        # If message is available, add to journal log
        if message:
            interaction = [{"message": message}]
            if response:
                meta_dict['Response'] = response
                
            self._save_journal_log(interaction, meta_dict)
            
            # Check if we should generate a journal entry
            self.check_journal()
            
    def _save_journal_log(self, interaction: List[dict], metadata: Optional[dict] = None) -> None:
        """
        Save journal log entries.
        
        Args:
            interaction (List[dict]): List of interaction dictionaries with 'message' key.
            metadata (dict, optional): Additional metadata to include.
        """
        collection_name = self.log_collection_name
        metadata_extra = metadata or {}
        
        for entry in interaction:
            chat_message = entry
            response_message = metadata_extra.get('Response', '')
            
            self.logger.debug(
                f"Saving to Journal Log: {collection_name}\nMessage: {chat_message}\nResponse: {response_message}",
            )
            
            self._save_to_journal(collection_name, chat_message, response_message, metadata_extra)
            
    def _save_to_journal(self, collection_name: str, chat_message: dict, 
                         response_message: str, metadata_extra: Optional[dict] = None) -> None:
        """
        Save a message to a specific collection in memory.
        
        Args:
            collection_name (str): Name of the collection to save to.
            chat_message (dict): The chat message to save.
            response_message (str): The response message to save.
            metadata_extra (dict, optional): Additional metadata to include.
        """
        collection_size = self.storage.search_metadata_min_max(collection_name, 'id', 'max')
        
        if collection_size is None or "target" not in collection_size:
            memory_id = ["1"]
            collection_int = 1
        else:
            collection_int = collection_size["target"] + 1 if collection_size["target"] is not None else 1
            memory_id = [str(collection_int)]
            
        metadata = {
            "id": collection_int,
            "Response": response_message,
        }
        
        if metadata_extra:
            metadata.update(metadata_extra)
            
        message = [chat_message["message"]]
        
        self.storage.save_to_storage(
            collection_name=collection_name,
            data=message,
            ids=memory_id,
            metadata=[metadata]
        )
            
    def check_journal(self) -> Optional[str]:
        """
        Check if it's time to write a journal entry and do so if necessary.
        
        Returns:
            Optional[str]: The generated journal entry if created, None otherwise.
        """
        count = self.storage.count_collection(self.log_collection_name)
        self.logger.debug(f"Journal log count: {count}")
        
        # Generate a journal entry if there are enough logs (default: 100)
        if count >= 100:
            return self.do_journal()
        
        return None
        
    def do_journal(self) -> str:
        """
        Execute the full journaling process: write entry, reflect, save, and store in database.
        
        Returns:
            str: The generated journal entry.
        """
        self.logger.info("Generating journal entry")
        
        # Write the journal entry
        self.write_entry()
        
        # Reflect on the entry
        self.journal_reflect()
        
        # Save the journal to a file
        try:
            path = self.save_journal()
            self.logger.info(f"Journal file created: {path}")
            self.filepath = path
        except Exception as e:
            self.logger.error(f"Error saving journal file: {e}")
        
        # Store in database
        self.journal_to_db()
        
        # Clear the log collection
        self.storage.delete_collection(self.log_collection_name)
        
        return self.results
        
    def write_entry(self) -> str:
        """
        Generate a new journal entry using the JournalAgent.
        
        Returns:
            str: The generated journal entry.
        """
        log = self.storage.load_collection(collection_name=self.log_collection_name)
        messages = self._format_journal_entries_for_agent(log)
        self.results = self.journal_agent.run(chat_log=messages)
        return self.results
        
    def journal_reflect(self) -> dict:
        """
        Reflect on the generated journal entry using the JournalThoughtAgent.
        The results are parsed and added to metadata.
        
        Returns:
            dict: Parsed thoughts about the journal entry.
        """
        thoughts = self.journal_thought.run(journal_entry=self.results)
        language, content = self.parser.extract_code_block(thoughts)
        self.thoughts = self.parser.parse_by_format(content, language)
        return self.thoughts
        
    def save_journal(self) -> str:
        """
        Save the journal entry to a unique markdown file.
        
        Returns:
            str: The path of the created file.
        """
        folder_path = os.path.join(os.getcwd(), 'Journal')
        file_name = datetime.now().strftime('%Y-%m-%d')
        
        # Ensure the folder exists, create it if not
        os.makedirs(folder_path, exist_ok=True)
        
        # Find existing files with the same name prefix
        existing_files = [f for f in os.listdir(folder_path) if f.startswith(file_name) and f.endswith(".md")]
        
        # Generate a unique file name based on the count of existing files
        unique_file_name = file_name
        if existing_files:
            count = len(existing_files)
            unique_file_name = f"{file_name}_{count}"
            
        # Create the file path
        file_path = os.path.join(folder_path, unique_file_name + ".md")
        
        # Write the content to the file
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.results)
            
        return file_path
        
    def journal_to_db(self) -> None:
        """
        Store the journal entry and its chunks in the database.
        """
        # Save whole entry
        source_id = self.storage.count_collection(self.whole_entries_collection)
        source_id_string = [str(source_id + 1)]
        
        metadata = {
            "id": source_id + 1,
            "Source": self.filepath,
        }
        
        if self.thoughts:
            metadata.update(self.thoughts)
            
        self.storage.save_to_storage(
            collection_name=self.whole_entries_collection,
            data=[self.results],
            ids=source_id_string,
            metadata=[metadata]
        )
        
        self.logger.debug(f"Saved journal entry with metadata: {metadata}")
        
        # Create and save semantic chunks for better retrieval
        chunks = chunker.semantic_chunk(self.results)
        
        for chunk in chunks:
            collection_size = self.storage.count_collection(self.chunks_collection)
            memory_id = [str(collection_size + 1)]
            
            chunk_metadata = {
                "id": collection_size + 1,
                "Source": self.filepath,
                "Source_ID": source_id + 1,
            }
            
            self.storage.save_to_storage(
                collection_name=self.chunks_collection,
                data=[chunk.content],
                ids=memory_id,
                metadata=[chunk_metadata]
            )
            
            self.logger.debug(f"Saved journal chunk: {chunk.content[:50]}...")
            
    def load_journals_from_backup(self, folder_path: str) -> None:
        """
        Load journal entries from markdown files in a specified folder.
        
        Args:
            folder_path (str): Path to the folder containing journal markdown files.
        """
        for filename in os.listdir(folder_path):
            # Check if the file has a .md extension
            if filename.endswith(".md"):
                file_path = os.path.join(folder_path, filename)
                self.filepath = os.path.abspath(file_path)
                
                # Read the contents of the file
                with open(self.filepath, "r", encoding="utf-8") as file:
                    file_contents = file.read()
                    
                self.logger.info(f"Loading journal from file: {filename}")
                
                self.results = file_contents
                self.journal_reflect()
                self.journal_to_db()
                
    def delete(self, ids: Union[str, list[str]] = None) -> None:
        """
        Delete journal entries and/or logs.
        
        Args:
            ids (Union[str, list[str]], optional): IDs of journal entries to delete.
                If None, removes all journal collections.
        """
        if ids is None:
            # Delete all journal collections
            self.storage.delete_collection(self.log_collection_name)
            self.storage.delete_collection(self.whole_entries_collection)
            self.storage.delete_collection(self.chunks_collection)
            self.logger.info("Deleted all journal collections")
        else:
            # Delete specific entries by ID
            self.storage.delete_from_storage(collection_name=self.whole_entries_collection, ids=ids)
            # Note: We can't easily delete the associated chunks, as the mapping is one-to-many
            self.logger.info(f"Deleted journal entries with IDs: {ids}")
            
    @staticmethod
    def _format_journal_entries(history):
        """
        Format journal entries for display to the user.
        
        Args:
            history (dict): Dictionary containing entry documents and metadata.
            
        Returns:
            str: Formatted journal entries.
        """
        formatted_entries = []
        
        for i, metadata in enumerate(history.get('metadatas', [])):
            entry_details = []
            
            # Start with User and Message
            entry_details.append(f"User: {metadata.get('User', 'N/A')}")
            entry_details.append(
                f"Message: {history['documents'][i] if i < len(history.get('documents', [])) else 'N/A'}"
            )
            
            # Add Inner Thought and Response if available
            if 'InnerThought' in metadata:
                entry_details.append(f"Inner Thought: {metadata['InnerThought']}")
            if 'Response' in metadata:
                entry_details.append(f"Response: {metadata['Response']}")
                
            # Add other fields
            for key, value in metadata.items():
                if key not in ["User", "id", "isotimestamp", "unixtimestamp", "InnerThought", "Response"]:
                    entry_details.append(f"{key}: {value}")
                    
            formatted_entries.append("\n".join(entry_details) + "\n")
            
        return "=====\n".join(formatted_entries).strip()
        
    @staticmethod
    def _format_journal_entries_for_agent(history):
        """
        Format journal entries for sending to the journal agent.
        
        Args:
            history (dict): Dictionary containing entry documents and metadata.
            
        Returns:
            str: Formatted journal entries optimized for the journal agent.
        """
        channel_entries = {}
        excluded_metadata = ["id", "response", "reason", "unixtimestamp", "mentions"]
        
        # Group entries by channel
        for i, entry in enumerate(history.get('metadatas', []), start=1):
            document_id = i - 1
            document = ""
            if 'documents' in history and 0 <= document_id < len(history['documents']):
                document = history['documents'][document_id]
                
            entry_details = []
            if document:
                entry_details.append(f"Message: {document}")
                
            channel = entry.get("channel", "")
            if channel not in channel_entries:
                channel_entries[channel] = []
                
            for key, value in entry.items():
                if key.lower() not in excluded_metadata:
                    entry_details.append(f"{key.capitalize()}: {value}")
                    
            channel_entries[channel].append((entry.get("id", 0), "\n".join(entry_details)))
            
        # Format entries grouped by channel and ordered by ID
        formatted_entries = []
        for channel, entries in channel_entries.items():
            entries.sort(key=lambda x: x[0])  # Sort by ID within each channel
            channel_formatted_entries = [entry[1] for entry in entries]
            formatted_entries.append(f"Channel: {channel}\n=====\n" + "\n=====\n".join(channel_formatted_entries))
            
        return "\n\n".join(formatted_entries).strip() 