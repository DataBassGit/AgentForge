# PersonaMemory

The `PersonaMemory` class is a specialized memory system for managing persona-related facts and generating dynamic persona narratives. It extends the base `Memory` class and integrates with specialized agents to provide intelligent persona management.

## Overview

PersonaMemory uses three specialized agents to:
1. **Retrieve** relevant persona facts through semantic search
2. **Generate** narrative summaries of the persona
3. **Update** persona facts based on new context

This creates a dynamic persona system that evolves based on interactions while maintaining coherent narratives for prompt injection.

## Key Features

- **Semantic Search**: Uses a Retrieval Agent to generate optimal search queries for finding relevant persona facts
- **Narrative Generation**: Automatically creates coherent persona narratives from static and dynamic facts
- **Intelligent Updates**: Determines when to add new facts or update existing ones
- **Fact Superseding**: Tracks when facts become outdated and manages fact evolution
- **Placeholder Integration**: Provides `{_mem.<node_id>._narrative}` and `{persona._static}` placeholders in prompt templates

## Configuration

### In a Cog YAML

```yaml
cog:
  name: "PersonaMemoryExample"
  persona: "default_assistant"
  
  agents:
    - id: understand
      template_file: UnderstandAgent
      
    - id: respond
      template_file: response_agent

  memory:
    - id: persona_memory
      type: agentforge.storage.persona_memory.PersonaMemory
      collection_id: persona_facts
      query_before: respond
      query_keys: [user_input]
      update_after: respond
      update_keys: [understand.insights, user_input]
      
  flow:
    start: understand
    transitions:
      understand: respond
      respond:
        end: true
```

## Agent Prompts

PersonaMemory requires three specialized agent prompts located in `.agentforge/prompts/persona/`:
- `persona_retrieval_agent.yaml`: Generates semantic search queries based on context and existing persona information.
- `persona_narrative_agent.yaml`: Creates coherent narratives combining static persona data with retrieved dynamic facts.
- `persona_update_agent.yaml`: Determines whether to add new facts, update existing ones, or take no action.

## Using Placeholders in Agent Prompts

```yaml
prompts:
  system:
    intro: |+
      You are a helpful assistant with evolving knowledge of the user.
    static_persona: |+
      ## Core Persona
      {persona._static}
    dynamic_persona: |+
      ## Dynamic Context
      {_mem.persona_memory._narrative}
  user:
    instruction: |+
      Respond to: {user_input}
      Use your understanding of the user's preferences and history to provide a personalized response.
```

## Memory Operations

### Query Operation

- `query_memory(query_keys, _ctx, _state, num_results=5)`
  - Combines query keys with static persona markdown
  - Uses the retrieval agent to generate semantic search queries
  - Retrieves and deduplicates persona facts
  - Uses the narrative agent to generate a coherent summary
  - Updates `.store` with `_narrative`, `_static`, and `_retrieved_facts`

### Update Operation

- `update_memory(update_keys, _ctx, _state, num_results=5)`
  - Combines update keys with context/state
  - Uses the update agent to determine whether to add or update facts
  - Stores new or updated facts with appropriate metadata

## Data Storage

PersonaMemory stores facts in ChromaDB with metadata such as:
```python
{
    'type': 'persona_fact',
    'source': 'update_agent',
    'superseded': False,  # or True if outdated
    'supersedes': 'fact_id1,fact_id2',  # If updating existing facts
    # Additional context fields as needed
}
```
> **Note:** Metadata fields may vary depending on the update action and code logic.

## Error Handling

- Errors are logged and raised as exceptions if specialized agents fail or if required data is missing.
- If no dynamic facts are found, a static-only narrative is generated.

## Example Workflow

1. User says: "I prefer Python over Java"
2. The understand agent extracts: `{ "preference": "Python over Java" }`
3. Before the respond agent, PersonaMemory queries for existing preferences
4. The narrative agent generates: "User is a Python enthusiast who values..."
5. The respond agent uses this narrative to provide a Python-focused response
6. After response, the update agent adds: "User prefers Python over Java for development"

## Integration with Other Memory Types

PersonaMemory can work alongside other memory types:

```yaml
memory:
  - id: general
    type: agentforge.storage.episodic.EpisodicMemory
    collection_id: conversations
  - id: persona_memory
    type: agentforge.storage.persona_memory.PersonaMemory
    collection_id: user_facts
```

This allows you to maintain conversation history while building an evolving persona model. 