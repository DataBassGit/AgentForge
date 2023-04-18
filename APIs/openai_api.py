import configparser
import openai
import json

# Read configuration file
config = configparser.ConfigParser()
config.read('Config/api_keys.ini')
openai.api_key = config.get('OpenAI', 'api_key')


def generate_text(prompt, model, params):
    response = openai.ChatCompletion.create(
        model=model,
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
