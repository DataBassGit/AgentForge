import requests
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'Config', '.env')  
load_dotenv(dotenv_path)
API_KEY = os.getenv('ANTHROPIC_API_KEY')

API_URL = "https://api.anthropic.com/v1/complete"

def generate_text(prompt, model, params):
    reply = None
    num_retries = 5  

    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        try:
            # Send request to API
            response = requests.post(API_URL, 
                headers={  
                    "X-API-Key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "model": model,
                    "max_tokens_to_sample": params["max_new_tokens"], 
                    "stop_sequences": ["\n\nHuman:"],
                    "temperature": params["temperature"],
                    "top_p": params["top_p"]  
                }
            )
            # Get response and extract completion
            response_data = response.json()
            reply = response_data["completion"]  
            break

        except requests.exceptions.HTTPError:
            if response.status_code == 502:  
                print("\n\nError: Bad gateway, retrying in {} seconds...".format(backoff))
                time.sleep(backoff)
            else:
                raise  

    if reply is None:
        raise RuntimeError("\n\nError: Failed to get Anthropic Response")

    return reply
