import configparser

config = configparser.ConfigParser()
config.read('Config/config.ini')
language_model_api = config.get('LanguageModelAPI', 'library')
