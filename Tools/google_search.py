import configparser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

config = configparser.ConfigParser()
config.read('Config/config.ini')

# Get the Google API key and Custom Search Engine ID from the config file
google_api_key = config.get('Google', 'api_key')
search_engine_id = config.get('Google', 'search_engine_id')


def google_search(query, num_results=5):
    try:
        # Initialize the Custom Search API service
        service = build("customsearch", "v1", developerKey=google_api_key)

        # Send the search query and retrieve the results
        result = service.cse().list(q=query, cx=search_engine_id, num=num_results).execute()

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

    # Return the list of search result URLs
    return search_results_links
