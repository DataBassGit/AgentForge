from typing import Dict, List
from Agents.Func.initialize_agent import set_model_api
from Agents.Func.initialize_agent import language_model_api
from Utilities.storage_interface import StorageInterface
from Personas.load_persona_data import load_persona_data

# Load persona data
persona_data = load_persona_data('Personas/default.json')
params = persona_data['ExecutionAgent']['Params']
objective = persona_data['Objective']


class ExecutionAgent:
    generate_text = None
    storage = None

    def __init__(self):
        # Add your initialization code here
        self.generate_text = set_model_api()
        self.storage = StorageInterface()

    def run_execution_agent(self, feedback) -> str:
        self.storage.sel_collection("tasks")

        print(f"\nFeedback: {feedback}\n")

        try:
            context = self.storage.get_storage().get()['documents']
        except Exception as e:
            context = []
        print(f"\nContext: {context}")

        try:
            task = self.storage.get_storage().get()['documents'][0]
        except Exception as e:
            print("failed to get task:", e)
            task = objective
        print(f"\nTask: {task}")

        system_prompt = persona_data['ExecutionAgent']['Prompts']['SystemPrompt'].format(objective=objective)
        context_prompt = persona_data['ExecutionAgent']['Prompts']['ContextPrompt'].format(context=context)
        instruction_prompt = persona_data['ExecutionAgent']['Prompts']['InstructionPrompt'].format(task=task)

        if feedback is None:
            feedback_prompt = ""
        else:
            feedback_prompt = persona_data['ExecutionAgent']['Prompts']['FeedbackPrompt'].format(feedback=feedback)

        prompt = [
            {"role": "system",
             "content": f"{system_prompt}"},
            {"role": "user",
             "content": f"{context_prompt}"
                        f"{instruction_prompt}"
                        f"{feedback_prompt}"},

        ]
        print(f"\nPrompt: {prompt}")

        result = self.generate_text(prompt, params).strip()

        print(f"\n\nExec: {result}")

        try:
            self.storage.sel_collection("results")
            self.storage.save_results(result, "results")
        except Exception as e:
            self.storage.create_col("results")
            self.storage.save_results(result, "results")

        return result
