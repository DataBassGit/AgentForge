from agentforge.modules.Actions import Action

objective = 'Stay up to date with current world events'
action = Action()
result = action.auto_execute(objective=objective)
print(f'\nAction Results: {result}')
