from flask import Flask, request, jsonify

from agentforge.agent.actionselection import ActionSelectionAgent
from agentforge.agent.actionpriming import ActionPrimingAgent
from agentforge.agent.status import StatusAgent
from agentforge.agent.summarization import SummarizationAgent
from agentforge.agent.execution import ExecutionAgent
from agentforge.agent.taskcreation import TaskCreationAgent
from agentforge.agent.reflexion import ReflexionAgent

app = Flask(__name__)

# load all agents
select_agent = ActionSelectionAgent()
prime = ActionPrimingAgent()
status = StatusAgent()
summ = SummarizationAgent()
execu = ExecutionAgent()
task = TaskCreationAgent()
reflex = ReflexionAgent()

@app.route('/select', methods=['POST'])
def select():
    data = request.get_json()
    context = data.get('context')
    result = select_agent.select(context)  # Replace with appropriate method call
    return jsonify(result=result)

@app.route('/prime', methods=['POST'])
def prime():
    data = request.get_json()
    context = data.get('context')
    result = prime_agent.prime(context)  # Replace with appropriate method call
    return jsonify(result=result)

@app.route('/status', methods=['POST'])
def status():
    data = request.get_json()
    context = data.get('context')
    result = status_agent.status(context)  # Replace with appropriate method call
    return jsonify(result=result)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    context = data.get('context')
    result = summ_agent.summarize(context)  # Replace with appropriate method call
    return jsonify(result=result)

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    context = data.get('context')
    result = execu_agent.execute(context)  # Replace with appropriate method call
    return jsonify(result=result)

@app.route('/task', methods=['POST'])
def task():
    data = request.get_json()
    context = data.get('context')
    result = task_agent.task(context)  # Replace with appropriate method call
    return jsonify(result=result)

@app.route('/reflex', methods=['POST'])
def reflex():
    data = request.get_json()
    context = data.get('context')
    result = reflex_agent.reflex(context)  # Replace with appropriate method call
    return jsonify(result=result)


@app.route('/test', methods=['GET'])
def test():
    return jsonify(message="Test endpoint is working!")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
