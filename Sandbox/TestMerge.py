from agentforge.modules.KnowledgeTraversal import merge_dictionaries_by_new_ids

if __name__ == '__main__':
    initial = {
        "ids": [
            ["91cb2744-3422-4fb3-81b9-fa342cb9f88a", "50522cd9-8072-482c-82d4-43c693aa8d41"]
        ],
        "distances": [[0.7611361145973206, 0.7611361145973206]],
        "metadatas": [
            [
                {
                    "framework": "Reflexion",
                    "id": "91cb2744-3422-4fb3-81b9-fa342cb9f88a",
                    "object": "Reflexion framework",
                    "predicate": "plays a crucial role in",
                    "purpose": "providing valuable feedback for future trials",
                    "reason": "This sentence highlights the crucial role of the Self-Reflection model in generating "
                              "verbal self-reflections for valuable feedback in future trials.",
                    "reasoning": "The Self-Reflection model is a key component of the Reflexion framework.",
                    "role": "generating verbal self-reflections",
                    "sentence": "The Self-Reflection model instantiated as an LLM plays a crucial role in the "
                                "Reflexion framework by generating verbal self-reflections to provide valuable "
                                "feedback for future trials.",
                    "source_name": "Test",
                    "source_url": "Reflexion - Language Agents with Verbal Reinforcement Learning.txt",
                    "subject": "Self-Reflection model",
                    "timestamp": "2024-03-02 17:19:00",
                },
                {
                    "generates": "verbal self-reflections",
                    "id": "50522cd9-8072-482c-82d4-43c693aa8d41",
                    "object": "LLM",
                    "predicate": "is instantiated as",
                    "purpose": "to provide valuable feedback for future trials",
                    "reason": "This sentence highlights the crucial role of the Self-Reflection model in generating "
                              "verbal self-reflections for valuable feedback in future trials.",
                    "role": "plays a crucial role in the Reflexion framework",
                    "sentence": "The Self-Reflection model instantiated as an LLM plays a crucial role in the "
                                "Reflexion framework by generating verbal self-reflections to provide valuable "
                                "feedback for future trials.",
                    "source_name": "Test",
                    "source_url": "Reflexion - Language Agents with Verbal Reinforcement Learning.txt",
                    "subject": "Self-Reflection model",
                    "timestamp": "2024-03-02 17:17:16",
                },
            ]
        ],
        "embeddings": None,
        "documents": [
            [
                "The Self-Reflection model instantiated as an LLM plays a crucial role in the Reflexion framework by "
                "generating verbal self-reflections to provide valuable feedback for future trials.",
                "The Self-Reflection model instantiated as an LLM plays a crucial role in the Reflexion framework by "
                "generating verbal self-reflections to provide valuable feedback for future trials.",
            ]
        ],
        "uris": None,
        "data": None,
    }

    sub = {
        "ids": [
            [
                "91cb2744-3422-4fb3-81b9-fa342cb9f88a",
                "980fd981-d98c-4f58-90df-4e6ecfda4a26",
                "bdee439a-9d65-4247-a5d9-01846cc09480",
            ]
        ],
        "distances": [[0.7611361145973206, 1.0017322301864624, 1.0017322301864624]],
        "metadatas": [
            [
                {
                    "framework": "Reflexion",
                    "id": "91cb2744-3422-4fb3-81b9-fa342cb9f88a",
                    "object": "Reflexion framework",
                    "predicate": "plays a crucial role in",
                    "purpose": "providing valuable feedback for future trials",
                    "reason": "This sentence highlights the crucial role of the Self-Reflection model in generating verbal self-reflections for valuable feedback in future trials.",
                    "reasoning": "The Self-Reflection model is a key component of the Reflexion framework.",
                    "role": "generating verbal self-reflections",
                    "sentence": "The Self-Reflection model instantiated as an LLM plays a crucial role in the Reflexion framework by generating verbal self-reflections to provide valuable feedback for future trials.",
                    "source_name": "Test",
                    "source_url": "Reflexion - Language Agents with Verbal Reinforcement Learning.txt",
                    "subject": "Self-Reflection model",
                    "timestamp": "2024-03-02 17:19:00",
                },
                {
                    "Actor component": "<DESCRIPTION OF ACTOR COMPONENT>",
                    "NLP": "<DESCRIPTION OF NLP>",
                    "Reflexion framework": "<DESCRIPTION OF REFLEXION FRAMEWORK>",
                    "id": "980fd981-d98c-4f58-90df-4e6ecfda4a26",
                    "object": "assessing the quality of the generated outputs produced by the Actor",
                    "predicate": "plays a crucial role in",
                    "reason": "This sentence introduces the Evaluator component, highlighting its critical role in assessing the quality of generated outputs.",
                    "sentence": "The Evaluator component of the Reflexion framework plays a crucial role in assessing the quality of the generated outputs produced by the Actor.",
                    "source_name": "Test",
                    "source_url": "Reflexion - Language Agents with Verbal Reinforcement Learning.txt",
                    "subject": "Evaluator component",
                    "timestamp": "2024-03-02 17:18:42",
                },
                {
                    "Actor": "Evaluator component",
                    "Reflexion framework": "Evaluator component",
                    "generated outputs": "Evaluator component",
                    "id": "bdee439a-9d65-4247-a5d9-01846cc09480",
                    "object": "assessing the quality of the generated outputs produced by the Actor",
                    "predicate": "plays a crucial role in",
                    "quality": "Evaluator component",
                    "reason": "This sentence introduces the Evaluator component, highlighting its critical role in assessing the quality of generated outputs.",
                    "sentence": "The Evaluator component of the Reflexion framework plays a crucial role in assessing the quality of the generated outputs produced by the Actor.",
                    "source_name": "Test",
                    "source_url": "Reflexion - Language Agents with Verbal Reinforcement Learning.txt",
                    "subject": "Evaluator component",
                    "timestamp": "2024-03-02 17:20:33",
                },
            ]
        ],
        "embeddings": None,
        "documents": [
            [
                "The Self-Reflection model instantiated as an LLM plays a crucial role in the Reflexion framework by generating verbal self-reflections to provide valuable feedback for future trials.",
                "The Evaluator component of the Reflexion framework plays a crucial role in assessing the quality of the generated outputs produced by the Actor.",
                "The Evaluator component of the Reflexion framework plays a crucial role in assessing the quality of the generated outputs produced by the Actor.",
            ]
        ],
        "uris": None,
        "data": None,
    }

    final = merge_dictionaries_by_new_ids(initial, sub)

    print(final)
