from .agent import Agent



class TaskCreationAgent(Agent):

    def load_data_from_memory(self,task):

        result_collection = self.storage.load_collection({
            'collection_name': "results",
            'include': ["documents"]
        })

        try:
            result = result_collection[0] if result_collection else ["No results found"]
        except Exception as e:
            result = ["No results found"]

        task_collection = self.storage.load_collection({
            'collection_name': task,
            'include': ["documents"],
        })

        x = 0
        task_list = []
        for task in task_collection['documents']:
            task_list.append(f"{x+1}. {task_collection['documents'][x]}")
            x += 1
        # print(task_list)
        # task_list = [task['documents'] for task in task_collection]

        # task_list = task_collection if task_collection else []
        # task = task_list[0] if task_collection else None

        return {'result': result, 'task_list': task_list}

    def parse_output(self, result, bot_id, data):
        new_tasks = result.split("\n")

        result = [{"task_desc": task_desc} for task_desc in new_tasks]
        filtered_results = [task for task in result if task['task_desc'] and task['task_desc'][0].isdigit()]

        try:
            order_tasks = [{
                'task_order': int(task['task_desc'].split('. ', 1)[0]),
                'task_desc': task['task_desc'].split('. ', 1)[1]
            } for task in filtered_results]
        except Exception as e:
            raise ValueError(f"\n\nError ordering tasks. Error: {e}")

        return {"tasks": order_tasks}

