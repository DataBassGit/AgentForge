from agentforge.agent import Agent
import os
from datetime import datetime
import agentforge.tools.semantic_chunk as chunker
from agentforge.utils.parsing_processor import ParsingProcessor


class Journal:
    """
    Manages the creation, storage, and retrieval of journal entries.
    """

    def __init__(self, chroma_instance):
        """
        Initialize the Journal with necessary components for storage, parsing, and agent interactions.
        """
        print("Journal initializing")
        self.storage = chroma_instance
        self.parse = ParsingProcessor()
        self.journal_agent = Agent(agent_name="JournalAgent")
        self.journal_thought = Agent(agent_name="JournalThoughtAgent")
        self.results = ''
        self.filepath = ''
        self.thoughts = None

    def do_journal(self):
        """
        Execute the full journaling process: write entry, reflect, save, and store in database.

        Returns:
            str: The generated journal entry.
        """
        print("Do Journal")
        self.write_entry()
        print("Write Entry")
        self.journal_reflect()
        print("Journal Reflect")
        try:
            path = self.save_journal()
            print(f"File created: {path}")
        except Exception as e:
            print(f"Exception occurred {e}")
        self.journal_to_db()
        return self.results

    def write_entry(self):
        """
        Generate a new journal entry using the JournalAgent.

        Returns:
            str: The generated journal entry.
        """
        collection = 'journal_log_table'
        print("Write Entry Collection")
        log = self.storage.load_collection(collection_name=collection)
        print("Write Entry Log")
        messages = self.format_journal_entries(log)
        self.results = self.journal_agent.run(chat_log=messages)
        return self.results

    def journal_reflect(self):
        """
        Reflect on the generated journal entry using the JournalThoughtAgent.
        The results are parsed and added to metadata.

        Returns:
            dict: Parsed thoughts about the journal entry.
        """
        thoughts = self.journal_thought.run(journal_entry=self.results)
        language, content = self.parse.extract_code_block(thoughts)
        self.thoughts = self.parse.parse_by_format(content, language)
        return self.thoughts

    def save_journal(self):
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

    def journal_to_db(self):
        """
        Store the journal entry and its chunks in the database.
        """
        # whole entry
        source_id = self.storage.count_collection('whole_journal_entries')
        source_id_string = [str(source_id + 1)]
        metadata = {
            "id": source_id + 1,
            "Source": self.filepath,
        }
        metadata.update(self.thoughts)
        self.storage.save_memory(collection_name='whole_journal_entries', data=self.results, ids=source_id_string, metadata=[metadata])
        print(f"Saved journal entry:\n\n{self.results}\nMetadata:\n{metadata}\n-----")

        # chunked for lookup
        chunks = chunker.semantic_chunk(self.results)

        for chunk in chunks:
            collection_size = self.storage.count_collection('journal_chunks_table')
            memory_id = [str(collection_size + 1)]
            metadata = {
                "id": collection_size + 1,
                "Source": self.filepath,
                "Source_ID": source_id + 1,
            }
            print(f"Saved chunk:\n\n{chunk.content}\nMetadata:\n{metadata}\n=====")

            self.storage.save_memory(collection_name='journal_chunks_table', data=chunk.content, ids=memory_id, metadata=[metadata])

    def load_journals_from_backup(self, folder_path):
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

                # Print the file contents
                print(f"Contents of {filename}:")
                print(file_contents)
                print("---")
                self.results = file_contents
                self.journal_reflect()
                self.journal_to_db()

    @staticmethod
    def format_journal_entries(history):
        """
        Formats chat logs for sending to the journal agent. The list is grouped by channel then ordered by ID.

        Args:
            history (dict): The history dictionary containing 'documents', 'ids', and 'metadatas'.

        Returns:
            str: Formatted general history entries.
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


if __name__ == '__main__':
    # Loads Journals from saved journal entries.
    # This will send each journal to the LLM and generate
    # thoughts, in a similar manner to the thought agent.
    # All journals must be .md files.
    from agentforge.storage.chroma_storage import ChromaStorage
    # TODO: Replace 'cog_name' and 'persona_name' with actual values from config or runtime context
    chroma = ChromaStorage.get_or_create(cog_name="cog_name", persona="persona_name")
    journal = Journal(chroma)
    folder_path2 = "..\\Journal"
    journal.load_journals_from_backup(folder_path2)