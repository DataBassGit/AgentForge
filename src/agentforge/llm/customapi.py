import requests
import json
import os

def request_completion(prompt):
    url = os.getenv('CUSTOM_AI_ENDPOINT')
    if not url:
        raise ValueError("The CUSTOM_AI_ENDPOINT environment variable is not set")
    headers = {'Content-Type': 'application/json'}
    data = {
        "temperature": 0.8,
        "model": "Open-Orca/OpenOrcaxOpenChat-Preview2-13B",
        "prompt": f"User: {prompt}Assistant:",
        "max_tokens": 2048,
        "stream": False
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        return None

# Example usage:
prompt = "What does the cow say?"
print(request_completion(prompt))
print("Done!")
