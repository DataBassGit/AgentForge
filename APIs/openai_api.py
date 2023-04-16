import configparser
import openai
import json

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/config.ini')
OPENAI_API_KEY = config.get('OpenAI', 'api_key')
MODEL_ID = config.get('OpenAI', 'fast_model')

# Initialize OpenAI library
openai.api_key = OPENAI_API_KEY


def generate_text(prompt, params):
    response = openai.ChatCompletion.create(
        model=MODEL_ID,
        messages=prompt,
        max_tokens=params["max_new_tokens"],
        n=params["n"],
        temperature=params["temperature"],
        top_p=params["top_p"],
        presence_penalty=params["penalty_alpha"],
        stop=params["stop"],
    )

    reply = response.choices[0].message.content
    return reply
