from Agents.execution_agent import ExecutionAgent
from Agents.task_creation_agent import TaskCreationAgent
from Agents.prioritization_agent import PrioritizationAgent
from Agents.salience_agent import SalienceAgent
from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface

# Load Agents
storage = StorageInterface()
taskCreationAgent = TaskCreationAgent()
prioritizationAgent = PrioritizationAgent()
executionAgent = ExecutionAgent()
salienceAgent = SalienceAgent()

# Add a variable to set the mode
functions = Functions()
functions.set_auto_mode()

# Salience loop
while True:

    collection_list = storage.storage_utils.collection_list()
    print(f"\nList: {collection_list}")

    peek = storage.storage_utils.peek("results")['documents']
    print(f"\nPeak Results: {peek}")

    peek = storage.storage_utils.peek("tasks")['documents']
    print(f"\nPeak Tasks: {peek}")

    text = "As an AI tasked with developing"
    res = storage.storage_utils.query_db("results", text)['documents']

    print(f"\nres:{res}")
    quit()

    pass


