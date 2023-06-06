import unittest

from agentforge.agent.salience_agent import SalienceAgent
from agentforge.agent.status_agent import StatusAgent
from agentforge.logs.logger_config import Logger
from agentforge.utils.function_utils import Functions
from agentforge.utils.storage_interface import StorageInterface


class MySalienceAgent(unittest.TestCase):
    def test_run(self):
        logger = Logger(name="Salience")
        logger.set_level('info')

        # Load Agents
        storage = StorageInterface()
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

            data = salienceAgent.run(feedback=feedback)

            logger.log(f"Data: {data}", 'debug')

            status = statusAgent.run(data)


if __name__ == '__main__':
    unittest.main()
