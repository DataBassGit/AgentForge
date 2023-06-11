from agentforge.agent.agent import Agent

agent = Agent('ExecutionAgent')

memory = {
    "collection_name": 'results',
    "data": 'Testing memory save',
    "desc": 'First memory',
    "ids": 'isdhgfoiasdhflaisdfh'
}

agent.storage.save_memory(memory)

memory = {
    "collection_name": 'results',
    "data": 'Testing memory save again bitch',
    "desc": 'Second memory',
    "ids": 'sikdfjgfbjkjgajksd'
}

agent.storage.save_memory(memory)


params = {
    "collection_name": 'results',
    # "ids": ['isdhgfoiasdhflaisdfh', 'sikdfjgfbjkjgajksd'],
    'filter': {'desc': "memory"}
}

mem = agent.storage.load_memory(params)

print(f'Mem: {mem}')

