from Agents.execution_agent import ExecutionAgent
from Agents.task_creation_agent import TaskCreationAgent
from Agents.prioritization_agent import PrioritizationAgent
from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface

# Load Agents
storage = StorageInterface()
executionAgent = ExecutionAgent()
taskCreationAgent = TaskCreationAgent()
prioritizationAgent = PrioritizationAgent()

# Add a variable to set the mode
functions = Functions()
functions.set_auto_mode()

# Main loop
while True:
    # Create task list
    taskCreationAgent.run_task_creation_agent()

    # Prioritize task list
    prioritizationAgent.run_prioritization_agent()

    # Allow for feedback if auto mode is disabled
    feedback = functions.check_auto_mode()

    # Run Execution Agent
    executionAgent.run_execution_agent(feedback)


