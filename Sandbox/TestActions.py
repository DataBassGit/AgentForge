from agentforge.modules.Actions import Actions

objective = 'Find news about the Ukraine war'
context = 'make sure that the news is within the last 15 days. Provide links to sources'
# context = None
threshold = 0.9

action = Actions()
result = action.auto_execute(objective, context, threshold)
print(f'\nAction Results: {result}')
