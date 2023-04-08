from typing import Dict, List
from oobabooga_api import generate_text

def task_creation_agent(objective: str, result: Dict, task_description: str, task_list: List[str], params: Dict):
    prompt = (
        f"You are an task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective}, "
        f"The last completed task has the result: {result}. This result was based on this task description: {task_description}. "
        f"These are incomplete tasks: {', '.join(task_list)}. "
        f"Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks. Return the tasks as an array."
    )
    new_tasks = generate_text(prompt, params).strip().split("\n")
    return [{"task_name": task_name} for task_name in new_tasks]

def prioritization_agent(this_task_id: int, task_list: List, objective: str, params: Dict):
    task_names = [t["task_name"] for t in task_list]
    next_task_id = int(this_task_id) + 1
    prompt = (
        f"""You are an task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks: {task_names}. """
        f"""Consider the ultimate objective of your team:{objective}. Do not remove any tasks. Return the result as a numbered list, like:
    #. First task
    #. Second task
    Start the task list with number {next_task_id}."""
    )
    new_tasks = generate_text(prompt, params).strip().split("\n")
    task_list = []
    for task_string in new_tasks:
        task_parts = task_string.strip().split(".", 1)
        if len(task_parts) == 2:
            task_id = task_parts[0].strip()
            task_name = task_parts[1].strip()
            task_list.append({"task_id": task_id, "task_name": task_name})
    return task_list

def execution_agent(objective: str, task: str, context: List, params: Dict) -> str:
    prompt = (
        f"You are an AI who performs one task based on the following objective: {objective}.\n"
        f"Take into account these previously completed tasks: {context}\n"
        f"Your task: {task}\nResponse:"
    )
    return generate_text(prompt, params).strip()

def context_agent(query: str, index: str, n: int, get_ada_embedding, pinecone_index):
    query_embedding = get_ada_embedding(query)
    results = pinecone_index.query(
        query_embedding.tolist(), top_k=n, include_metadata=True
    )
    sorted_results = sorted(
        results.matches, key=lambda x: x.score, reverse=True
    )
    return [str(item.metadata["task"]) for item in sorted_results]
