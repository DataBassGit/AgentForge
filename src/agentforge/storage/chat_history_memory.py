import uuid
from agentforge.storage.memory import Memory
from agentforge.utils.prompt_processor import PromptProcessor

class ChatHistoryMemory(Memory):

    ALLOW_META = {"iso_timestamp", "id", }

    def __init__(self, cog_name, persona=None, collection_id="chat_history"):
        super().__init__(cog_name, persona, collection_id, logger_name="ChatHistoryMemory")
        self.prompt_processor = PromptProcessor()

    def update_memory(self, ctx, output):
        turn_id = str(uuid.uuid4())

        def make_meta(role):
            return {
                "role": role,
                "turn_id": turn_id,
            }

        docs  = [self.prompt_processor.value_to_markdown(ctx), self.prompt_processor.value_to_markdown(output)]
        metas = [make_meta("user"), make_meta("assistant")]

        # Let Chroma auto-increment the integer IDs (or keep your own counter),
        # but *do not* copy the partner’s text into metadata.
        self.storage.save_to_storage(self.collection_name,
                                    data=docs,
                                    metadata=metas)

    def query_memory(self, num_results=20, **kwargs):
        raw = self.storage.get_last_x_entries(
            self.collection_name,
            num_results,
            include=["documents", "metadatas"]
        )

        records = [
            {"content": d, "meta": m}
            for d, m in list(zip(raw["documents"], raw["metadatas"]))
        ]

        # Sort records by iso_timestamp (chronological order, oldest first)
        # If iso_timestamp is missing, fallback to id (should be monotonically increasing)
        def sort_key(rec):
            meta = rec["meta"]
            # Prefer iso_timestamp if present, else fallback to id
            # If both missing, fallback to 0
            ts = meta.get("iso_timestamp")
            if ts is not None:
                return ts
            return meta.get("id", 0)

        records = sorted(records, key=sort_key)

        history = []

        for rec in records:
            current_record = {}
            role = rec["meta"]["role"]

            current_record[role] = [
                rec["content"],
                f"timestamp: {rec['meta'].get('iso_timestamp', '')}\n"
            ]

            history.append(current_record)

        self.store["history"] = history