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
        # but *do not* copy the partner's text into metadata.
        self.storage.save_to_storage(self.collection_name,
                                    data=docs,
                                    metadata=metas)

    # ------------------------
    # Helpers
    # ------------------------
    def _sort_records(self, records):
        """Return records sorted oldest→newest using iso_timestamp then id."""
        def sort_key(rec):
            meta = rec["meta"]
            ts = meta.get("iso_timestamp")
            return ts if ts is not None else meta.get("id", 0)
        return sorted(records, key=sort_key)

    def _format_records(self, records):
        """Convert raw records into the structure expected by prompts."""
        formatted = []
        for rec in records:
            role = rec["meta"]["role"]
            formatted.append({
                role: [
                    rec["content"],
                    f"timestamp: {rec['meta'].get('iso_timestamp', '')}\n"
                ]
            })
        return formatted

    def _get_recency_records(self, num_results):
        raw = self.storage.get_last_x_entries(
            self.collection_name,
            num_results,
            include=["documents", "metadatas"],
        )
        records = [
            {"content": d, "meta": m}
            for d, m in zip(raw["documents"], raw["metadatas"])
        ]
        return self._sort_records(records)

    def _get_semantic_records(self, query_texts, max_retrieval, recency_records):
        # Calculate a filter to avoid fetching items already in the recency slice
        min_id = None
        if recency_records:
            try:
                min_id = min(r["meta"]["id"] for r in recency_records)
            except Exception:
                pass

        filter_condition = {"id": {"$lt": min_id}} if min_id is not None else None

        # Ask for more than we need to account for post-deduplication
        overshoot = max_retrieval + len(recency_records) * 2

        raw_semantic = self.storage.query_storage(
            collection_name=self.collection_name,
            query=query_texts,
            filter_condition=filter_condition,
            num_results=overshoot,
        )

        if not raw_semantic or not raw_semantic.get("documents"):
            return []

        seen_ids = {r["meta"]["id"] for r in recency_records}
        seen_turns = {r["meta"].get("turn_id") for r in recency_records}

        semantic_records = []
        for d, m in zip(raw_semantic["documents"], raw_semantic["metadatas"]):
            if m["id"] in seen_ids or m.get("turn_id") in seen_turns:
                continue
            semantic_records.append({"content": d, "meta": m})

        # Sort and limit to the requested max number
        semantic_records = self._sort_records(semantic_records)[:max_retrieval]
        return semantic_records

    # ------------------------
    # Public
    # ------------------------
    def query_memory(self, num_results=20, max_retrieval=20, query_keys=None, _ctx=None, _state=None, **kwargs):
        """Populate self.store with 'history' (recency) and optionally 'relevant' (semantic)."""
        # Phase 1 – recency slice
        recency_records = self._get_recency_records(num_results)
        self.store["history"] = self._format_records(recency_records)

        # Phase 2 – semantic slice
        if max_retrieval > 0:
            query_texts = self._build_queries_from_keys_and_context(query_keys, _ctx, _state)
            # Fallback: if no query text provided, use the most recent user message
            if not query_texts:
                # find last record authored by user (search from end)
                for rec in reversed(recency_records):
                    if rec["meta"].get("role") == "user":
                        query_texts = rec["content"]
                        break
                # If still empty, take last assistant message as last resort
                if not query_texts and recency_records:
                    query_texts = recency_records[-1]["content"]
            if query_texts:
                semantic_records = self._get_semantic_records(query_texts, max_retrieval, recency_records)
                if not semantic_records:
                    semantic_records = [{"content": "No relevant records found in memory", "meta": {"role": "memory_system"}}]

                self.store["relevant"] = self._format_records(semantic_records)