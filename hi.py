from Utilities.function_utils import Functions
from Utilities.storage_interface import StorageInterface
from Agents.heuristic_comparator_agent import HeuristicComparatorAgent
from Agents.heuristic_check_agent import HeuristicCheckAgent
from Agents.heuristic_reflection_agent import HeuristicReflectionAgent
from flask import Flask, request

app = Flask(__name__)

# Load Agents
storage = StorageInterface()
heuristic_comparator_agent = HeuristicComparatorAgent()
heuristic_check_agent = HeuristicCheckAgent()
heuristic_reflection_agent = HeuristicReflectionAgent()

# Add a variable to set the mode
functions = Functions()
feedback = None


@app.route('/check', methods=['PUT'])
def run_check():
    data = request.get_json()
    # print(data)
    seta = data['seta']
    if data['botid'] is not None:
        botid = data['botid']
    else:
        botid = "undefined"
    # do something with the new string
    results=heuristic_check_agent.run_agent(seta, botid, feedback=feedback)
    return f"String updated: {results}"

@app.route('/reflect', methods=['PUT'])
def run_reflect():
    data = request.get_json()
    # print(f"\nReflect Data: {data}")
    seta = data['seta']
    if data['botid'] is not None:
        botid = data['botid']
    else:
        botid = "undefined"
    # do something with the new string
    results=heuristic_reflection_agent.run_agent(seta, botid, feedback=feedback)
    return f"String updated: {results}"

@app.route('/compare', methods=['PUT'])
def run_compare():
    data = request.get_json()
    print(data)
    seta = data['seta']
    setb = data['setb']
    if data['botid'] is not None:
        botid = data['botid']
    else:
        botid = "undefined"
    # do something with the new string
    results=heuristic_comparator_agent.run_agent(seta, setb, botid, feedback=feedback)
    return f"String updated: {results}"


@app.route('/plot_dict', methods=['GET'])
def display_plot_dict():
    storage.storage_utils.select_collection('results')
    # storage.storage_utils.collection.get()
    search = storage.storage_utils.collection.get(include=["embeddings"])
    embeddings = search.get('embeddings',[])
    print(embeddings)
    return {'embeddings': embeddings}

@app.route('/bot_dict', methods=['GET'])
def display_bot_dict():
    botid = request.args.get('botid')
    storage.storage_utils.select_collection('results')
    search = storage.storage_utils.collection.get(where={"botid": botid},include=["embeddings", "documents", "metadatas"])
    print(search)
    return search

if __name__ == '__main__':
    app.run()



