from Agents.Func.initialize_config import language_model_api


def set_model_api():
    if language_model_api == 'oobabooga_api':
        from APIs.oobabooga_api import generate_text
    elif language_model_api == 'openai_api':
        from APIs.openai_api import generate_text
    else:
        raise ValueError(f"Unsupported Language Model API library: {language_model_api}")
    return generate_text
