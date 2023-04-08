import configparser
import openai

# Read configuration file
config = configparser.ConfigParser()
config.read('config.ini')
OPENAI_API_KEY = config.get('OpenAI', 'api_key')
MODEL_ID = config.get('OpenAI', 'model_id')

# Initialize OpenAI library
openai.api_key = OPENAI_API_KEY



def generate_text(prompt, params):
    response = openai.Completion.create(
        engine="davinci-codex",
        prompt=prompt,
        max_tokens=params["max_new_tokens"],
        n=params["n"],
        temperature=params["temperature"],
        top_p=params["top_p"],
        repetition_penalty=params["repetition_penalty"],
        presence_penalty=params["penalty_alpha"],
        stop=params["stop"],
        seed=params["seed"],
    )

    reply = response.choices[0].text.strip()
    return reply
