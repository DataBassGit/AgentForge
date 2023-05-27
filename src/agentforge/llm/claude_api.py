import os
import anthropic

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'Config', '.env')  
load_dotenv(dotenv_path)
API_KEY = os.getenv('ANTHROPIC_API_KEY')

client = anthropic.Client(API_KEY)

def generate_text(prompt, model, params):
    reply = None
    num_retries = 5 

    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        try:            
            response = client.completion(
                prompt=prompt,
                stop_sequences=[anthropic.HUMAN_PROMPT],  
                model=model,
                max_tokens_to_sample=params["max_new_tokens"],  
                temperature=params["temperature"],
                top_p=params["top_p"]  
            )
            reply = response  
            break

        except anthropic.HTTPError:
            if response.status_code == 502:   
                print("\n\nError: Bad gateway, retrying in {} seconds...".format(backoff))
                time.sleep(backoff)
            else:
                raise    

    if reply is None:
        raise RuntimeError("\n\nError: Failed to get Anthropic Response")

    return reply
