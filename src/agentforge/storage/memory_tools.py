from agentforge.utils.logger import Logger
from agentforge.utils.parsing_processor import ParsingProcessor
from agentforge.agent import Agent
import re


class AdvancedMemoryFunctions:

    def __init__(self, chroma_instance):
        self.memory = chroma_instance
        self.logger = Logger('Memory')
        self.parser = ParsingProcessor()

    def combine_and_rerank(self, query_results: list, rerank_query, num_results=5):
        """
        Combine multiple query results, rerank them based on a new query, and return the top results.

        This function takes multiple query results, combines them, and then reranks the combined
        results based on a new query. It's useful for refining search results across multiple
        collections or queries.

        Args:
            query_results (list): A list of query result dictionaries, each containing 'ids',
                                'embeddings', 'documents', and 'metadatas'.
            rerank_query (str): The query string used for reranking the combined results.
            num_results (int, optional): The number of top results to return after reranking.
                                        Defaults to 5.

        Returns:
            dict: A dictionary containing the reranked results, including 'ids', 'embeddings',
                'documents', and 'metadatas' for the top results.

        Raises:
            ValueError: If query_results is empty or if reranking fails.

        Example:
            query_results = [results1, results2, results3]
            rerank_query = "specific query that can be the same or a new query"
            reranked = query_and_rerank(query_results, rerank_query, num_results=3)
        """

        # Combine all query results
        combined_query_results = self.memory.combine_query_results(*query_results)

        reranked_results = self.memory.rerank_results(
            query_results=combined_query_results,
            query=rerank_query,
            temp_collection_name="temp_reranking_collection",
            num_results=num_results
        )

        return reranked_results

    def reask(self):
        pass


class ScratchPad:
    def __init__(self, chroma_instance):
        self.memory = chroma_instance
        self.logger = Logger('Memory')
        self.parser = ParsingProcessor()

    def save_scratchpad_log(self, pad_log_name, content):
        """
        Save or update the scratchpad log for a specific scratchpad.

        Args:
            pad_log_name (str): The collection to save the scratchpad log to.
            content (str): The content to save in the scratchpad log.
        """
        collection_name = pad_log_name
        collection_name = self.parser.format_string(collection_name)

        collection_size = self.memory.count_collection(collection_name)
        memory_id = [str(collection_size + 1)]
        self.logger.log(f"Saving Scratchpad Log to: {collection_name}\nMessage:\n{content}\nID: {memory_id}", 'debug', 'Memory')
        self.memory.save_memory(collection_name=collection_name, data=[content], ids=memory_id)

    def save_scratchpad(self, pad_name, content):
        """
        Save or update a specific scratchpad.

        Args:
            pad_name (str): The username to save the scratchpad for.
            content (str): The content to save in the scratchpad.
        """
        collection_name = pad_name

        self.memory.save_memory(collection_name=collection_name, data=[content], ids=["1"])

    def get_scratchpad_log(self, pad_log_name):
        """
        Retrieve the scratchpad log for a specific user.

        Args:
            pad_log_name (str): The username to retrieve the scratchpad log for.

        Returns:
            list: The scratchpad log entries as a list or an empty list if not found.
        """
        collection_name = pad_log_name
        collection_name = self.parser.format_string(collection_name)
        result = self.memory.load_collection(collection_name=collection_name)
        self.logger.log(f"Scratchpad Log: {result}", 'debug', 'Memory')
        if result and result['documents']:
            return result['documents']
        return []

    def get_scratchpad(self, pad_name):
        """
        Retrieve the scratchpad for a specific user.

        Args:
            pad_name (str): The username to retrieve the scratchpad for.

        Returns:
            str: The scratchpad content or a default message if not found.
        """
        collection_name = pad_name
        collection_name = self.parser.format_string(collection_name)
        result = self.memory.load_collection(collection_name=collection_name)
        if result and result['documents']:
            return result['documents'][0]
        return "No information available yet. This scratchpad will be updated as we learn more about the user."

    def check_scratchpad(self, pad_name):
        """
        Check if it's time to update the scratchpad for a specific user and do so if necessary.

        Args:
            pad_name (str): The username to check the scratchpad for.

        Returns:
            str or None: Updated scratchpad content if updated, None otherwise.
        """
        self.logger.log(f"Checking scratchpad for user: {pad_name}", 'debug', 'Memory')

        scratchpad_log = self.get_scratchpad_log(pad_name)
        self.logger.log(f"Scratchpad log entries: {len(scratchpad_log)}", 'debug', 'Memory')
        for entry in scratchpad_log:
            self.logger.log(f"Scratchpad log entry: {entry}", 'debug', 'Memory')
        count = len(scratchpad_log)

        self.logger.log(f"Number of entries in scratchpad log: {count}", 'debug', 'Memory')

        if count >= 10:
            self.logger.log(f"Scratchpad log count >= 10, updating scratchpad", 'debug', 'Memory')

            scratchpad_agent = Agent(agent_name="ScratchpadAgent")

            current_scratchpad = self.get_scratchpad(pad_name)
            self.logger.log(f"Current scratchpad content: {current_scratchpad[:100]}...", 'debug', 'Memory')

            scratchpad_log_content = "\n".join(scratchpad_log)
            self.logger.log(f"Scratchpad log content: {scratchpad_log_content[:100]}...", 'debug', 'Memory')

            agent_vars = {
                "scratchpad_log": scratchpad_log_content,
                "scratchpad": current_scratchpad
            }
            scratchpad_result = scratchpad_agent.run(**agent_vars)
            self.logger.log(f"Scratchpad agent result: {scratchpad_result[:100]}...\nVars: {agent_vars}", 'debug', 'Memory')

            updated_scratchpad = self.extract_updated_scratchpad(scratchpad_result)
            self.logger.log(f"Updated scratchpad content: {updated_scratchpad[:100]}...", 'debug', 'Memory')

            self.save_scratchpad(pad_name, updated_scratchpad)
            self.logger.log(f"Saved updated scratchpad for user: {pad_name}", 'debug', 'Memory')

            # Clear the scratchpad log after processing
            collection_name = f"scratchpad_log_{pad_name}"
            collection_name = self.parser.format_string(collection_name)
            self.memory.delete_collection(collection_name)
            self.logger.log(f"Cleared scratchpad log for user: {pad_name}", 'debug', 'Memory')

            return updated_scratchpad

        self.logger.log(f"Scratchpad log count < 10, no update needed", 'debug', 'Memory')
        return None

    def extract_updated_scratchpad(self, scratchpad_result: str) -> str:
        """
        Extracts the updated scratchpad content from the ScratchpadAgent's output.

        Parameters:
        - scratchpad_result (str): The full output from the ScratchpadAgent.

        Returns:
        - str: The extracted updated scratchpad content.
        """
        pattern = r'<updated_scratchpad>(.*?)</updated_scratchpad>'
        match = re.search(pattern, scratchpad_result, re.DOTALL)

        if match:
            return match.group(1).strip()
        else:
            self.logger.log("No updated scratchpad content found in the result.", 'warning', 'Formatting')
            return ""


class Journal:
    def __init__(self, chroma_instance):
        self.memory = chroma_instance
        self.logger = Logger('Memory')
        self.parser = ParsingProcessor()

    def save_journal_log(self, interaction, metadata):
        """
        Save journal log entries.
        """
        collection_name = 'journal_log_table'
        metadata_extra = {}
        for query, response in enumerate(interaction):
            if metadata:
                metadata_extra = metadata
            self.logger.log(f"Saving Channel to: {collection_name}\nMessage:\n{query}",
                            'debug', 'Memory')
            self.save_to_journal(collection_name, query, response, metadata_extra)

    def recall_journal_entry(self, message, categories, num_entries: int = 2):
        """
        Recall journal entries based on a message and categories.

        Args:
            message (str): The message to use for recall.
            categories (str): Comma-separated list of categories.
            num_entries (int): Number of entries to recall. Defaults to 2.

        Returns:
            str: Formatted string of recalled journal entries.
        """
        self.logger.log(f"Recalling {num_entries} entries from the journal", 'debug', 'Memory')
        journal_query = f"{message}\n\n Related Categories: {categories}"
        collection_name = 'journal_chunks_table'
        journal_chunks = self.memory.query_memory(
            collection_name=collection_name,
            query=journal_query,
            num_results=num_entries
        )

        # Create a dictionary to store the recalled memories
        recalled_memories = {
            'ids': [],
            'embeddings': None,
            'metadatas': [],
            'documents': []
        }

        if journal_chunks:
            self.logger.log(f"Recalled Memories:\n{journal_chunks}", 'debug', 'Memory')

            # Set the relevance threshold
            relevance_threshold = 0.65  # Adjust this value as needed

            for i in range(len(journal_chunks['ids'])):
                distance = journal_chunks['distances'][i]
                if distance >= relevance_threshold:
                    source_id = journal_chunks['metadatas'][i]['Source_ID']

                    filters = {"id": {"$eq": source_id}}

                    # Retrieve the full journal entry based on the source_id
                    full_entry = self.memory.load_collection(
                        collection_name='whole_journal_entries',
                        where=filters
                    )

                    if full_entry:
                        print(f"Full Entry: {full_entry}")
                        # Add the relevant fields to the recalled_memories dictionary
                        recalled_memories['ids'].append(full_entry['ids'][0])
                        recalled_memories['metadatas'].append(
                            {key: value for key, value in full_entry['metadatas'][0].items() if
                             key.lower() not in ['source', 'isotimestamp', 'unixtimestamp']})
                        recalled_memories['documents'].append(full_entry['documents'][0])

            print(f"Full Entries Appended: {recalled_memories}")
            memories = self.format_journal_entries(recalled_memories)
            return memories
        else:
            memories = self.format_journal_entries(recalled_memories)
            return memories

    def check_journal(self):
        """
        Check if it's time to write a journal entry and do so if necessary.

        Returns:
            bool or None: True if journal was written, None otherwise.
        """
        count = self.memory.count_collection('journal_log_table')
        print(count)
        if count >= 100:
            from agentforge.storage.episodic_memory import Journal
            journal_function = Journal(self.memory)
            print("Journal initialized")
            journal_written = journal_function.do_journal()
            if journal_written:
                print("Deleting Journal collection")
                self.memory.delete_collection('journal_log_table')
            return journal_written
        else:
            return None

    def save_to_journal(self, collection_name: str, chat_message: dict, response_message: str,
                           metadata_extra=None):
        """
        Save a message to a specific collection in memory.

        Args:
            collection_name (str): Name of the collection to save to.
            chat_message (dict): The chat message to save.
            response_message (str): The response message to save.
            metadata_extra (dict, optional): Additional metadata to include.
        """
        collection_size = self.memory.search_metadata_min_max(collection_name, 'id', 'max')
        if collection_size is None or "target" not in collection_size:
            memory_id = ["1"]
            collection_int = 1
        else:
            memory_id = [str(collection_size["target"] + 1 if collection_size["target"] is not None else 1)]
            collection_int = collection_size["target"] + 1

        metadata = {
            "id": collection_int,
            "Response": response_message,
        }
        # Need to implement a last accessed metadata

        if metadata_extra:
            metadata.update(metadata_extra)

        message = [chat_message["message"]]
        self.memory.save_memory(collection_name=collection_name, data=message, ids=memory_id, metadata=[metadata])

    @staticmethod
    def format_journal_entries(history):
        formatted_entries = []
        for i, metadata in enumerate(history.get('metadatas', [])):
            entry_details = []
            # Start with User and Message
            entry_details.append(f"User: {metadata.get('User', 'N/A')}")
            entry_details.append(
                f"Message: {history['documents'][i] if i < len(history.get('documents', [])) else 'N/A'}")

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