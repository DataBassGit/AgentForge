import os
import requests

class BraveSearch:
    """
    A Python wrapper for the Brave Search API.

    This class provides methods to interact with the Brave Search API, allowing you to perform searches,
    retrieve search results, and access various features of the API.

    Attributes:
        base_url (str): The base URL for the Brave Search API.
        api_key (str): The API key for authentication.
        headers (dict): The headers to be used in API requests.

    Raises:
        ValueError: If the BRAVE_API_KEY environment variable is not set.
    """

    def __init__(self):
        self.base_url = 'https://api.search.brave.com'
        self.api_key = os.environ.get('BRAVE_API_KEY')
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY environment variable is not set")
        self.headers = {
            'X-Subscription-Token': self.api_key,
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip'
        }

    def search(self, query, **kwargs):
        """
        Perform a search using the Brave Search API and parse the results.

        Args:
            query (str): The search query.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: Parsed search results containing titles, URLs, descriptions, and extra snippets.

        Raises:
            requests.RequestException: If the API request fails.
            ValueError: If the response cannot be parsed or is invalid.
        """
        try:
            params = {'q': query}
            params.update(kwargs)

            response = requests.get(self.base_url + '/res/v1/web/search', params=params, headers=self.headers)
            response.raise_for_status()
            results = response.json()

            # Parse the search results
            parsed_results = {'web_results': [], 'video_results': []}

            # Extract web search results
            if 'web' in results and 'results' in results['web']:
                for result in results['web']['results']:
                    parsed_results['web_results'].append({
                        'type': 'web_result',
                        'title': result.get('title', 'No data'),
                        'url': result.get('url', 'No data'),
                        'description': result.get('description', 'No data'),
                        'extra_snippets': result.get('extra_snippets', ["No data"])
                    })

            # Extract video search results
            if 'videos' in results and 'results' in results['videos']:
                for result in results['videos']['results']:
                    parsed_results['video_results'].append({
                        'type': 'video_result',
                        'title': result.get('title', 'No data'),
                        'url': result.get('url', 'No data'),
                        'description': result.get('description', 'No data')
                    })

            return parsed_results

        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}") from e
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to parse API response: {str(e)}") from e

    def summarize(self, query, **kwargs):
        """
        Get an AI-generated summary for a query using the Summarizer API.

        Args:
            query (str): The search query.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: A dictionary containing the parsed summary information.

        Raises:
            requests.RequestException: If the API request fails.
            ValueError: If the response cannot be parsed or is invalid.
        """
        try:
            params = {'q': query, 'summary': 1}
            params.update(kwargs)

            response = requests.get(self.base_url + '/res/v1/web/search', params=params, headers=self.headers)
            response.raise_for_status()

            data = response.json()

            if data.get('type') == 'summarizer':
                summary_info = {
                    'status': data.get('status'),
                    'title': data.get('title'),
                    'summary': [msg.get('content') for msg in data.get('summary', [])],
                    'followups': data.get('followups', []),
                    'entities': data.get('entities_infos', {})
                }
                if 'enrichments' in data:
                    summary_info['enrichments'] = data['enrichments']
            elif data.get('type') == 'search':
                summary_info = {
                    'query': data.get('query', {}).get('original', ''),
                    'results': [],
                    'videos': []
                }

                # Handle web results
                for result in data.get('web', {}).get('results', []):
                    result_info = {
                        'type': 'web_result',
                        'title': result.get('title', ''),
                        'description': result.get('description', ''),
                        'url': result.get('url', '')
                    }
                    if 'extra_snippets' in result:
                        result_info['extra_snippets'] = result['extra_snippets']
                    summary_info['results'].append(result_info)

                # Handle video results
                for video in data.get('videos', {}).get('results', []):
                    video_info = {
                        'type': 'video_result',
                        'title': video.get('title', ''),
                        'description': video.get('description', ''),
                        'url': video.get('url', ''),
                        'thumbnail': video.get('thumbnail', {}).get('src', '')
                    }
                    summary_info['videos'].append(video_info)
            else:
                raise ValueError(f"Unexpected response type: {data.get('type')}")

            return summary_info

        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}") from e
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to parse API response: {str(e)}") from e

if __name__ == '__main__':

    brave = BraveSearch()
    import json

    # Perform a web search with additional parameters
    search_results = brave.search(query='OpenAI ChatGPT', count=5)
    print(json.dumps(search_results, indent=4))

    # Get an AI-generated summary with additional parameters
    summarize_result = brave.summarize(query='What is ChatGPT?')
    print(json.dumps(summarize_result, indent=4))
