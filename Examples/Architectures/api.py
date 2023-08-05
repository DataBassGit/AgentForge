from flask import Flask, request

from agentforge.agent.actionselection import ActionSelectionAgent
from agentforge.agent.actionpriming import ActionPrimingAgent
from agentforge.agent.status import StatusAgent
from agentforge.agent.task import TaskCreationAgent
from agentforge.agent.prioritization import PrioritizationAgent
from agentforge.agent.execution import ExecutionAgent
from agentforge.agent.summarization import SummarizationAgent
from agentforge.agent.reflexion import ReflexionAgent

app = Flask(__name__)

# load all agents
select = ActionSelectionAgent()
prime = ActionPrimingAgent()
status = StatusAgent()
summ = SummarizationAgent()
execu = ExecutionAgent()
task = TaskCreationAgent()
prior = PrioritizationAgent()
reflex = ReflexionAgent()

@app.route('/select' methods=['POST'])
def select():
    data = request.get_json()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port="5000")