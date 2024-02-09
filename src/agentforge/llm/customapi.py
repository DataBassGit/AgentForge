import requests
import json
import os
from agentforge.utils.functions.Logger import Logger

logger = Logger(name=__name__)


def request_completion(model_prompt, **params):
    log_level = params.get('log_level', 'info')
    logger.set_level(log_level)
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
    logger.log_response(response)

    if response.status_code == 200:
        return response.json()
    else:
        return None


# ----------------------------------------------------------------------------------------------------
# Example usage:
# prompt = "What does the cow say?"
# print(request_completion(prompt))
# print("Done!")
