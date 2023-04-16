import json
import requests

# Server address
server = "127.0.0.1"

def generate_text(prompt, params):

    print("prompt:" + str(prompt))
    #print("\nparams:" + str(params + "\n"))
    
    params = {
    'max_new_tokens': 200,
    'do_sample': True,
    'temperature': 0.7,
    'top_p': 0.5,
    'typical_p': 1,
    'repetition_penalty': 1.2,
    'encoder_repetition_penalty': 1.0,
    'top_k': 40,
    'min_length': 0,
    'no_repeat_ngram_size': 2,
    'num_beams': 1,
    'penalty_alpha': 0,
    'length_penalty': 1.0,
    'early_stopping': False,
    'seed': -1,
    'add_bos_token': True,
    'custom_stopping_strings': [],
    'truncation_length': 2048,
    'ban_eos_token': False,
}

    # Input prompt
    prompt = "Create an asphalt project schedular web app that is interactive."

    payload = json.dumps([prompt, params])

    with requests.Session() as session:
        response = session.post(f"http://{server}:7860/run/textgen", json={
            "data": [
                payload
            ]
        }).json()
        
        #debug
        print(response)

        reply = response["data"][0]
    
    # Close the session
    #session.close()
    
    return reply
