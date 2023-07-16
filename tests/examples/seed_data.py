from agentforge.utils import storage_interface
from agentforge.agent.summarization import SummarizationAgent


def main():
    status = 'test status 321'
    task_id = '103'
    text = 'test text 124'
    task_order = '104'
    ordered_results = [
        {
            "Description": 'task abc',
            "Order": 110,
        },
        {
            "Description": 'task xyz',
            "Order": 111,
        },
    ]
    task_desc_list = ["do abc", "do xyz"]
    result = ['test results 127']

    test_agent = SummarizationAgent()
    storage = storage_interface.StorageInterface()

    #test_agent.save_tasks(ordered_results, task_desc_list)
    #test_agent.save_results(result)


    test_agent.save_status(status, "110", text, task_order)
    params = {
        "collection_name": "Tasks"
    }
    printtasks = storage.storage_utils.load_collection(params)
    params = {
        "collection_name": "Results"
    }
    printresults = storage.storage_utils.load_collection(params)
    print(printtasks)
    print(printresults)


if __name__ == '__main__':
    main()
