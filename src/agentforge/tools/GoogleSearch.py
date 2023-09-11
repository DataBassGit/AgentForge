import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

google_api_key = os.getenv('GOOGLE_API_KEY')
search_engine_id = os.getenv('SEARCH_ENGINE_ID')


def google_search(query, number_result=5):
    try:
        # Initialize the Custom Search API service
        service = build("customsearch", "v1", developerKey=google_api_key)

        # Send the search query and retrieve the results
        result = service.cse().list(q=query, cx=search_engine_id, num=number_result).execute()

        # Extract the search result items from the response
        search_results = result.get("items", [])

        # Create a list of only the URLs from the search results
        search_results_links = [(item["link"], item["snippet"]) for item in search_results]

    except HttpError as e:
        # Handle errors in the API call
        error_details = json.loads(e.content.decode())
        error_code = error_details.get("error", {}).get("code")
        error_message = error_details.get("error", {}).get("message", "")

        # Check if the error is related to an invalid or missing API key
        if error_code == 403 and "invalid API key" in error_message:
            return "Error: The provided Google API key is invalid or missing."
        else:
            return f"Error: {e}"

    parsed_results = parse_tool_results(search_results_links)

    # Return the list of search result URLs
    return parsed_results


def parse_tool_results(tool_result):
    if isinstance(tool_result, list):
        # Format each search result
        formatted_results = [f"URL: {url}\nDescription: {desc}\n---" for url, desc in tool_result]
        # Join all results into a single string
        final_output = "\n".join(formatted_results)
    else:
        final_output = tool_result

    return final_output
