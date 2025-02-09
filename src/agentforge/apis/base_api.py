import time
from openai import APIError, RateLimitError, APIConnectionError
from agentforge.utils.logger import Logger


class BaseModel:
    """
    A base class encapsulating shared logic (e.g., logging, retries, prompt building).
    Subclasses must implement the _call_api method, which does the actual work of sending prompts.
    """

    # Defaults you might share across all models
    default_retries = 8
    default_backoff = 2

    def __init__(self, model_name, **kwargs):
        self.logger = None
        self.allowed_params = None
        self.excluded_params = None
        self.model_name = model_name
        self.num_retries = kwargs.get("num_retries", self.default_retries)
        self.base_backoff = kwargs.get("base_backoff", self.default_backoff)

    def generate(self, model_prompt, **params):
        """
        Main entry point for generating responses. This method handles retries,
        calls _call_api for the actual request, and logs everything.
        """
        # Log the prompt once at the beginning
        self.logger = Logger(name=params.pop('agent_name', 'NamelessAgent'))
        self.logger.log_prompt(model_prompt)

        reply = None
        for attempt in range(self.num_retries):
            backoff = self.base_backoff ** (attempt + 1)
            try:
                reply = self._call_api(model_prompt, **params)
                # If successful, log and break
                self.logger.log_response(reply)
                break
            except (RateLimitError, APIConnectionError) as e:
                self.logger.log(f"Error: {str(e)}. Retrying in {backoff} seconds...", level="warning")
                time.sleep(backoff)
            except APIError as e:
                if getattr(e, "status_code", None) == 502:
                    self.logger.log(f"Error 502: Bad gateway. Retrying in {backoff} seconds...", level="warning")
                    time.sleep(backoff)
                else:
                    raise
            except Exception as e:
                # General catch-all for other providers
                self.logger.log(f"Error: {str(e)}. Retrying in {backoff} seconds...", level="warning")
                time.sleep(backoff)

        if reply is None:
            self.logger.log("Error: All retries exhausted. No response received.", level="critical")
        return reply

    @staticmethod
    def _prepare_prompt(model_prompt):
        # Format system/user messages in the appropriate style
        return [
            {"role": "system", "content": model_prompt.get('system')},
            {"role": "user", "content": model_prompt.get('user')}
        ]

    def _call_api(self, model_prompt, **params):
        # Step 1: Build or adapt the prompt in a way that the target model expects.
        prompt = self._prepare_prompt(model_prompt)

        # Step 2: Filter or transform the params so that you only pass what this model actually uses.
        filtered_params = self._prepare_params(**params)

        # Step 3: Call the actual API with the refined prompt and parameters.
        response = self._do_api_call(prompt, **filtered_params)
        return self._process_response(response)

    def _prepare_params(self, **params):
        if self.allowed_params:
            # Keep only parameters explicitly allowed
            return {k: v for k, v in params.items() if k in self.allowed_params}
        if self.excluded_params:
            # Exclude parameters listed in excluded_params
            return {k: v for k, v in params.items() if k not in self.excluded_params}
        # If neither allowed nor excluded parameters are defined, pass all params
        return params

    def _do_api_call(self, prompt, **filtered_params):
        # The actual request to the underlying client
        raise NotImplementedError("Subclasses must implement _do_call_api method.")

    def _process_response(self, raw_response):
        # Subclasses can process the raw responses as needed
        return raw_response
