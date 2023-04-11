from typing import Dict, List
from Agents.Func.initialize_agent import set_model_api
from Agents.Func.initialize_agent import language_model_api

generate_text = set_model_api()


def execution_agent(objective: str, task: str, context: List, params: Dict) -> str:

    if language_model_api == 'openai_api':
        prompt = [
            {"role": "system",
             "content": f"You are an AI who performs one task based on the following objective: {objective}.\n"},
            {"role": "user",
             "content": f"Take into account these previously completed tasks: {context}\nYour task: {task}\nResponse:"},
        ]
    elif language_model_api == 'oobabooga_api':
        prompt = (
            f"You are an AI who performs one task based on the following objective: {objective}.\n"
            f"Take into account these previously completed tasks: {context}\n"
            f"Your task: {task}\nResponse:"
        )
    else:
        print('\nLanguage Model Not Found!')
        raise ValueError('Language model not found. Please check the language_model_api variable.')

    return generate_text(prompt, params).strip()