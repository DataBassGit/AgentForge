from agentforge.modules.Actions import Actions

objective = 'Stay up to date with current world events'
action = Actions()
result = action.auto_execute(objective=objective)
print(f'\nAction Results: {result}')
