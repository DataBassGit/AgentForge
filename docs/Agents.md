# -=Agents=-
## ExecutionAgent

* Inputs: context, summary
* Sourced from database: objective, task
* User Input: feedback

## ReflexionAgent

* Inputs: context
* Sourced from database: objective, task
* User Input: feedback

## SearchSelector

* Inputs: context
* Sourced from Database: objective, current_task
* User Input:
* User or Database: task_result

## StatusAgent?

* Inputs: summary
* Sourced from database: summary, task, task_result, objective

## SummarizationAgent

* User or Database: text

## TaskCreationAgent

* Inputs: result
* Sourced from database: goal, task, task_list

# HeuristicComaratorAgent

* Inputs: seta, setb
* Sourced from database: heuristic_imperatives

# HuristicReflectionAgent

* Inputs: seta
* Sourced from database: heuristic_imperatives

# HeuristicCheckAgent

* Inputs: seta
* Sourced from database: heuristic_imperatives