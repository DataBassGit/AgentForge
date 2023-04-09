from typing import Dict, List
from Agents.Func.initialize_agent import set_model_api
from Agents.Func.initialize_agent import language_model_api

generate_text = set_model_api()


def task_creation_agent(objective: str, result: Dict, task_description: str, task_list: List[str], params: Dict):
    if language_model_api == 'openai_api':
        prompt = [
            {"role": "system",
             "content": f"You are a task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}, "},
            {"role": "user",
             "content": f"The last completed task has the result: {result}. This result was based on this task description: {task_description}. "
                        f"These are incomplete tasks: {', '.join(task_list)}. "
                        f"Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Return the tasks as an array."},
        ]
    elif language_model_api == 'oobabooga_api':
        prompt = (
            f"You are a task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}, "
            f"The last completed task has the result: {result}. This result was based on this task description: {task_description}. "
            f"These are incomplete tasks: {', '.join(task_list)}. "
            f"Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Return the tasks as an array."
        )
    else:
        print('\nLanguage Model Not Found!')
        raise ValueError('Language model not found. Please check the language_model_api variable.')

    new_tasks = generate_text(prompt, params).strip().split("\n")
    return [{"task_name": task_name} for task_name in new_tasks]
