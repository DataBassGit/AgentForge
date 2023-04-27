from Agents.execution_agent import ExecutionAgent
from Agents.task_creation_agent import TaskCreationAgent
from Agents.prioritization_agent import PrioritizationAgent
from Agents.salience_agent import SalienceAgent
from Agents.status_agent import StatusAgent
from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface

# Load Agents
storage = StorageInterface()
taskCreationAgent = TaskCreationAgent()
prioritizationAgent = PrioritizationAgent()
executionAgent = ExecutionAgent()
salienceAgent = SalienceAgent()
statusAgent = StatusAgent()

# Add a variable to set the mode
functions = Functions()
functions.set_auto_mode()

# Salience loop
while True:
    collection_list = storage.storage_utils.collection_list()

    # print(f"\nCollection List: {collection_list}")
    # quit()

    # Allow for feedback if auto mode is disabled
    feedback = functions.check_auto_mode()

    data = salienceAgent.run_salience_agent()

    print(f"\n\nSalience Agent - Data: {data}")
    # quit()

    statusAgent.run_status_agent(data)
    # quit()



