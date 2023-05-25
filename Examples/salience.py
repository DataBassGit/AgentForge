import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Agents.execution_agent import ExecutionAgent
from Agents.task_creation_agent import TaskCreationAgent
from Agents.prioritization_agent import PrioritizationAgent
from Agents.salience_agent import SalienceAgent
from Agents.status_agent import StatusAgent
from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface
from Logs.logger_config import Logger

logger = Logger(name="Salience")
logger.set_level('info')

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
status = None

# Salience loop
while True:
    collection_list = storage.storage_utils.collection_list()
    logger.log(f"Collection List: {collection_list}", 'debug')

    functions.show_tasks('Salience')
    # quit()
    # Allow for feedback if auto mode is disabled
    status_result = functions.check_status(status)
    if status_result is not None:
        feedback = functions.check_auto_mode(status_result)
    else:
        feedback = functions.check_auto_mode()

    data = salienceAgent.run_salience_agent(feedback=feedback)

    logger.log(f"Data: {data}", 'debug')

    status = statusAgent.run_status_agent(data)
    # quit()



