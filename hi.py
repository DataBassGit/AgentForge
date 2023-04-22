from Agents.execution_agent import ExecutionAgent
from Agents.task_creation_agent import TaskCreationAgent
from Agents.prioritization_agent import PrioritizationAgent
from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface
from Agents.heuristic_comparator_agent import HeuristicComparatorAgent

# Load Agents
storage = StorageInterface()
taskCreationAgent = TaskCreationAgent()
prioritizationAgent = PrioritizationAgent()
executionAgent = ExecutionAgent()
heuristic_comparator_agent = HeuristicComparatorAgent()

# Add a variable to set the mode
functions = Functions()
functions.set_auto_mode()

# Main loop
while True:
    # Create task list
    seta = input("provide example 1: ")
    setb = input("provide example 2: ")
    feedback = None

    heuristic_comparison = heuristic_comparator_agent.run_agent(seta, setb, feedback)
    print(heuristic_comparison)


