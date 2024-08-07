from agentforge.modules.Actions import Actions

objective = 'Automate file backup'
# context = 'Focus your scope on technology'
context = None
threshold = 0.5

action = Actions()
result = action.auto_execute(objective, context, threshold)
print(f'\nAction Results: {result}')
