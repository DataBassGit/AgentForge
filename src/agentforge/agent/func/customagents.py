def agentload (agentname,classname):
    import importlib
    agent = importlib.import_module(agentname)
    customclass = getattr(classname,agent)
    return customclass()

#


"""
 How to:
 First, import this library
 from agentforge.agent.customagents import agentload
 
 Then we instantiate the custom agent:
 custommodule = agentload(agentname)
 
 then we instantiate the class
 agentobject = custommodule.classname()
 
 Finally, we can call the custom agent
 customresult = agentobject.run(stuff)
"""

from agentforg.agent.reflexion import ReflexionAgent
result = ReflexionAgent.run()