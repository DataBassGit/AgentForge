import uuid
from agentforge.storage.memory import Memory
from agentforge.utils.prompt_processor import PromptProcessor

class ChatHistoryMemory(Memory):

    ALLOW_META = {"iso_timestamp", "id"}

    def __init__(self, cog_name, persona=None, collection_id="chat_history"):
        super().__init__(cog_name, persona, collection_id, logger_name="ChatHistoryMemory")
        self.prompt_processor = PromptProcessor()

    # def update_memory(self, _ctx, output, **kwargs):
    #     markdown_ctx = self.prompt_processor.value_to_markdown(_ctx)
    #     markdown_output = self.prompt_processor.value_to_markdown(output)
    #     data = [markdown_ctx, markdown_output]
    #     meta = [
    #         {"role": "user", "response": markdown_output},
    #         {"role": "assistant", "context": markdown_ctx}
    #     ]
    #     self.storage.save_to_storage(self.collection_name, data=data, metadata=meta)

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

    # def query_memory(self, num_results=10, **kwargs):
    #     raw = self.storage.get_last_x_entries(self.collection_name, num_results, include=['documents', 'metadatas'])
    #     documents = raw.get("documents", [])
    #     metadatas = raw.get("metadatas", [])

    #     entries = []
    #     for idx, (doc, meta) in enumerate(zip(documents, metadatas)):
    #         entry = {}
    #         entry["content"] = doc
    #         entry["metadata"] = meta
    #         entries.append(entry)
            
    #     self.store["history"] = entries

    def query_memory(self, num_results=10, **kwargs):
        raw = self.storage.get_last_x_entries(self.collection_name,
                                      num_results,
                                      include=["documents","metadatas"])

        # Older-to-newer, strip junk fields, group by turn_id
        records = [
            {"content": d, "meta": m}
            for d, m in list(zip(raw["documents"], raw["metadatas"]))
        ]

        history = []

        for rec in records:
            current_record = {}
            role = rec["meta"]["role"]
            # turn_id = rec["meta"]["turn_id"]

            # if turn_id != current_turn.get("turn_id"):
            #     # if current_turn:
            #     #     history.append(current_turn)          # push completed turn
            #     current_turn = {"turn_id": turn_id}

            if isinstance(rec["content"], str):
                content = rec["content"]
            elif isinstance(rec["content"], list):
                content = "\n".join(rec["content"])
            else:
                content = {k: v for k, v in rec["content"].items()}

            current_record[role] = {
                # "content": {rec['content']",
                "content": content,
                "metadata": {k: v for k, v in rec["meta"].items()
                            if k in self.ALLOW_META}
            }

            history.append(current_record)

        self.store["history"] = history