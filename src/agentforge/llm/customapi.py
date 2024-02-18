import requests
import json
import os
from agentforge.utils.functions.Logger import Logger

logger = Logger(name=__name__)


def request_completion(model_prompt, **params):
    """
    Sends a request to a custom AI model endpoint to generate a completion based on the provided prompt.

    This function constructs a request with specified parameters and sends it to a custom AI endpoint, which is
    expected to generate text based on the input prompt. The endpoint URL is read from an environment variable.

    Parameters:
        model_prompt (str): The prompt text to send to the model for generating a completion.
        **params: Arbitrary keyword arguments for future extensibility, not used currently.

    Returns:
        dict or None: The JSON response from the AI model if the request is successful, None otherwise.

    Logs the prompt and the response using a Logger instance. If the `CUSTOM_AI_ENDPOINT` environment variable
    is not set or if the request fails, appropriate error messages are logged.
    """
    logger.log_prompt(model_prompt)

    headers = {'Content-Type': 'application/json'}
    data = {
        "temperature": 0.8,
        "model": "Open-Orca/OpenOrcaxOpenChat-Preview2-13B",
        "prompt": f"User: {model_prompt}Assistant:",
        "max_tokens": 2048,
        "stream": False
    }

    url = os.getenv('CUSTOM_AI_ENDPOINT')
    if not url:
        logger.log("\n\nError: The CUSTOM_AI_ENDPOINT environment variable is not set", 'critical')

    response = requests.post(url, headers=headers, data=json.dumps(data))
    logger.log_response(str(response))

    if response.status_code == 200:
        return response.json()
    else:
        return None


# ----------------------------------------------------------------------------------------------------
# Example usage:
# prompt = "What does the cow say?"
# print(request_completion(prompt))
# print("Done!")
