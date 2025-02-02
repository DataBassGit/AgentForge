import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

def google_search(query, number_result=5):
    """
    Perform a Google search using the Custom Search API.

    Args:
        query (str): The search query.
        number_result (int, optional): The number of search results to return. Defaults to 5.

    Returns:
        str: A formatted string containing the search results or an error message.

    Raises:
        ValueError: If the GOOGLE_API_KEY or SEARCH_ENGINE_ID environment variables are not set.
        HttpError: If there's an error with the API request.
        Exception: For any other unexpected errors during execution.
    """
    google_api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('SEARCH_ENGINE_ID')

    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    if not search_engine_id:
        raise ValueError("SEARCH_ENGINE_ID environment variable is not set")

    try:
        # Initialize the Custom Search API service
        service = build("customsearch", "v1", developerKey=google_api_key)

        # Send the search query and retrieve the results
        result = service.cse().list(q=query, cx=search_engine_id, num=number_result).execute()

        # Extract the search result items from the response
        search_results = result.get("items", [])

        # Create a list of only the URLs from the search results
        search_results_links = [(item["link"], item["snippet"]) for item in search_results]

        return parse_tool_results(search_results_links)

    except HttpError as e:
        # Handle errors in the API call
        error_details = json.loads(e.content.decode())
        error_code = error_details.get("error", {}).get("code")
        error_message = error_details.get("error", {}).get("message", "")

        # Check if the error is related to an invalid or missing API key
        if error_code == 403 and "invalid API key" in error_message:
            return "Error: The provided Google API key is invalid or missing."
        else:
            return f"Error: {str(e)}"

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def parse_tool_results(tool_result):
    """
    Parse and format the search results.

    Args:
        tool_result (list or str): The search results to parse.

    Returns:
        str: A formatted string containing the parsed search results.
    """
    if isinstance(tool_result, list):
        # Format each search result
        formatted_results = [f"URL: {url}\nDescription: {desc}\n---" for url, desc in tool_result]
        # Join all results into a single string
        final_output = "\n".join(formatted_results)
    else:
        final_output = tool_result

    return final_output
