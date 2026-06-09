from .base_api import BaseModel
import litellm  # type: ignore[reportMissingImports]


class LiteLLM(BaseModel):
    @staticmethod
    def _prepare_prompt(model_prompt):
        return model_prompt

    def _do_api_call(self, prompt, **filtered_params):
        logger = self.logger
        if logger is None:
            raise RuntimeError("LiteLLM logger was not initialized before provider execution.")

        url = filtered_params.pop("host_url", None)
        try:
            endpoint = filtered_params.pop("endpoint")
        except KeyError as e:
            logger.critical(f"Missing required parameter (endpoint): {e}")
        messages_dict = prompt.get("messages", {})

        system_text = messages_dict.get("system")
        user_text = messages_dict.get("user")

        messages = []
        if system_text:
            messages.append({"role": "system", "content": system_text})
        if user_text:
            messages.append({"role": "user", "content": user_text})

        data = {"model": f"{endpoint}/{self.model_name}", "messages": messages, **filtered_params}
        # litellm._turn_on_debug()

        try:
            if url:
                response = litellm.completion(
                    api_base=url, model=data["model"], messages=data["messages"], **filtered_params
                )
            else:
                response = litellm.completion(model=data["model"], messages=data["messages"], **filtered_params)
        except litellm.AuthenticationError as e:
            # Thrown when the API key is invalid
            print(f"Authentication failed: {e}")
            return None
        except litellm.RateLimitError as e:
            # Thrown when you've exceeded your rate limit
            print(f"Rate limited: {e}")
            return None
        except litellm.APIError as e:
            # Thrown for general API errors
            print(f"API error: {e}")
            return None

        if response.model_extra:
            # return error content
            logger.info(
                f"""Request usage:
            
                Completion tokens: {response.usage.completion_tokens}
                Prompt tokens: {response.usage.prompt_tokens}"""
            )
            print(
                f"""Request usage:
            
                Completion tokens: {response.usage.completion_tokens}
                Prompt tokens: {response.usage.prompt_tokens}"""
            )

        return response.json()

    def _process_response(self, raw_response):
        # Handle different Ollama endpoint responses
        if raw_response is None:
            return None
        if "response" in raw_response:  # /api/generate
            return raw_response["response"]
        elif "message" in raw_response:  # /api/chat
            return raw_response["message"]["content"]
        elif "choices" in raw_response:
            return raw_response["choices"][0]["message"]["content"]
        else:
            logger = self.logger
            if logger is not None:
                logger.error(f"Unexpected Ollama response format: {raw_response}")
            return None
