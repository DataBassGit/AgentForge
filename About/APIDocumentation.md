# API Documentation:

This API includes several endpoints that provide functionality for running various agents and displaying data.

## Endpoint: /check

Method: PUT

Input:

* seta (required): a string that will be processed by the heuristic check agent
* botid (optional): a string that identifies the bot being used. If not provided, "undefined" will be used as the default value.
Output:

* The results of running the heuristic check agent on the provided input string.


## Endpoint: /reflect

Method: PUT

Input:

* seta (required): a string that will be processed by the heuristic reflection agent
* botid (optional): a string that identifies the bot being used. If not provided, "undefined" will be used as the default value.
Output:

* The results of running the heuristic reflection agent on the provided input string.


## Endpoint: /compare

Method: PUT

Input:

* seta (required): the first string to be compared
* setb (required): the second string to be compared
* botid (optional): a string that identifies the bot being used. If not provided, "undefined" will be used as the default value.
Output:

* The results of running the heuristic comparator agent on the provided input strings.


## Endpoint: /plot_dict

Method: GET

Input: None

Output:

* A dictionary containing a list of embeddings obtained from the "results" collection in the database.


## Endpoint: /bot_dict

Method: GET

Input:

* botid (required): a string that identifies the bot to retrieve data for.
Output:

* A dictionary containing the embeddings, documents, and metadata associated with the specified botid in the "results" collection in the database.
