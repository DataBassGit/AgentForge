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
- **Placeholder Integration**: Provides `{memory.<node_id>._narrative}` and `{persona._static}` placeholders

## Configuration

### In a Cog YAML

```yaml
cog:
  name: "PersonaMemoryExample"
  persona: "default_assistant"  # Optional: Override system default

  agents:
    - id: understand
      template_file: UnderstandAgent
    - id: respond
      template_file: response_agent

  memory:
    - id: persona_memory
      type: agentforge.storage.persona_memory.PersonaMemory
      collection_id: user_persona_facts  # Optional: Custom collection name
      query_before: respond  # Query before this agent runs
      query_keys: [user_input]  # Context keys for queries
      update_after: respond  # Update after this agent completes
      update_keys: [understand.insights, user_input]  # Data to consider for updates

  flow:
    start: understand
    transitions:
      understand: respond
      respond:
        end: true
```

### Direct Usage

```python
from agentforge.storage.persona_memory import PersonaMemory

# Create a PersonaMemory instance
memory = PersonaMemory(
    cog_name="my_cog",
    persona="AssistantPersona",
    collection_id="custom_facts"
)

# Query for persona narrative
result = memory.query_memory("User asks about preferences")
narrative = result['_narrative']
static_persona = result['_static']

# Update with new information
memory.update_memory({
    'user_preference': 'prefers detailed explanations',
    'interaction': 'asked about machine learning'
})
```

## Agent Prompts

PersonaMemory requires three specialized agent prompts located in `.agentforge/prompts/persona/`:

### retrieval_agent.yaml
Generates semantic search queries based on context and existing persona information.

### narrative_agent.yaml
Creates coherent narratives combining static persona data with retrieved dynamic facts.

### update_agent.yaml
Determines whether to add new facts, update existing ones, or take no action.

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
      {memory.persona_memory._narrative}
      
  user:
    instruction: |+
      Respond to: {user_input}
      
      Use your understanding of the user's preferences and history to provide 
      a personalized response.
```

## Memory Operations

### Query Operation

1. **Context Preparation**: Combines query text with static persona markdown
2. **Query Generation**: Retrieval Agent generates 1-3 semantic search queries
3. **Fact Retrieval**: Performs searches and deduplicates results
4. **Narrative Generation**: Narrative Agent creates a coherent summary
5. **Result Storage**: Updates internal store with narrative and facts

### Update Operation

1. **Context Analysis**: Combines update data with existing context
2. **Fact Retrieval**: Searches for related existing facts
3. **Action Decision**: Update Agent determines action (add/update/none)
4. **Storage Update**: 
   - **Add**: Creates new fact with metadata
   - **Update**: Adds new fact and marks old ones as superseded
   - **None**: No changes made

## Data Storage

PersonaMemory stores facts in ChromaDB with the following metadata:

```python
{
    'type': 'persona_fact',
    'source': 'update_agent',
    'superseded': False,  # or True if outdated
    'supersedes': 'fact_id1,fact_id2',  # If updating existing facts
    'context_<key>': 'value'  # Truncated context data
}
```

## Best Practices

1. **Query Keys**: Choose context keys that provide relevant information for persona queries
2. **Update Keys**: Select data that contains potential persona-relevant information
3. **Collection Naming**: Use descriptive collection IDs to organize different persona aspects
4. **Agent Tuning**: Customize the specialized agent prompts for your specific use case
5. **Fact Management**: Periodically review stored facts to ensure quality

## Error Handling

PersonaMemory includes robust error handling:

- **JSON Parsing**: Falls back to direct parsing if ParsingProcessor fails
- **Agent Errors**: Falls back to base Memory class implementation
- **No Results**: Generates static-only narratives when no dynamic facts exist
- **Missing Agents**: Raises clear errors if specialized agents can't be loaded

## Example Workflow

1. User asks: "I prefer Python over Java"
2. Cog's understand agent extracts: `{'preference': 'Python over Java'}`
3. Before respond agent, PersonaMemory queries for existing preferences
4. Narrative Agent generates: "User is a Python enthusiast who values..."
5. Respond agent uses this narrative to provide Python-focused response
6. After response, Update Agent adds: "User prefers Python over Java for development"

## Integration with Existing Memory Types

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

This allows you to maintain conversation history while building a evolving persona model. 