from openai import OpenAI
import tiktoken
import os
import time

from dotenv import load_dotenv
load_dotenv()

DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
DEFAULT_CHAT_MODEL = "gpt-4o-mini"

def count_tokens(text, model_name="gpt-4o"):
    encoder = tiktoken.encoding_for_model(model_name)
    tokens = encoder.encode(text)
    return len(tokens)

def count_convo_tokens(messages,model_name="gpt-4o"):
    ans = 0
    for m in messages:
        ans += count_tokens(m['content'],model_name)
    return ans

def truncate_text_by_tokens(text, max_tokens, model_name="gpt-4o"):
    if count_tokens(text, model_name) <= max_tokens:
        return text
    encoder = tiktoken.encoding_for_model(model_name)
    tokens = encoder.encode(text)
    truncated_tokens = tokens[:max_tokens]
    truncated_text = encoder.decode(truncated_tokens)
    return f"{truncated_text}"

import os
import random
from typing import Dict, Any, List
from together import Together
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_together import ChatTogether
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages.base import BaseMessage
import re 
import json 

# even in case of offered free costs, we calculate the standard cost
MODEL_COST_PER_MILLION = {
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": {"input": 3.5, "output": 3.5},
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": {"input": 0.88, "output": 0.88},
    "deepseek-ai/DeepSeek-V3": {"input": 1.25, "output": 1.25},
    "Qwen/Qwen2.5-7B-Instruct-Turbo": {"input": 0.3, "output": 0.3},
    "Qwen/QwQ-32B": {"input": 1.2, "output": 1.2},
    "mistralai/Mistral-7B-Instruct-v0.3": {"input": 0.2, "output": 0.2},
    "mistralai/Mistral-Small-24B-Instruct-2501": {"input": 0.8, "output": 0.8},
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": {"input": 0.18, "output": 0.18},
    "meta-llama/Llama-3.2-3B-Instruct-Turbo": {"input": 0.06, "output": 0.06},
    "google/gemma-2-9b-it": {"input": 0.3, "output": 0.3},
    "google/gemma-2-27b-it": {"input": 0.8, "output": 0.8},
    "gemini-2.0-flash": {"input": 0.1, "output": 0.4},
    "deepseek/deepseek-chat-v3-0324:free": {"input": 0.27, "output": 1.10},
    "meta-llama/llama-4-maverick:free": {"input": 0, "output": 0},
    "meta-llama/llama-4-scout:free": {"input": 0, "output": 0},
    "google/gemini-2.5-pro-exp-03-25:free": {"input": 1.25, "output": 10.00},
    "mistralai/mistral-small-3.1-24b-instruct:free": {"input": 0.8, "output": 0.8},
    "google/gemma-3-1b-it:free": {"input": 0, "output": 0},
    "google/gemma-3-4b-it:free": {"input": 0, "output": 0},
    "google/gemma-3-12b-it:free": {"input": 0, "output": 0},
    "google/gemma-3-27b-it:free":  {"input": 0.12, "output": 0.12},
    "deepseek/deepseek-r1-zero:free": {"input": 0.55, "output": 2.19},
    "qwen/qwq-32b:free": {"input": 1.2, "output": 1.2},
    "deepseek/deepseek-r1:free": {"input": 0.55, "output": 2.19},
    "deepseek/deepseek-chat:free": {"input": 0.27, "output": 1.10},
    "meta-llama/llama-3.3-70b-instruct:free": {"input": 0.88, "output": 0.88},
    "qwen/qwen-2.5-7b-instruct:free": {"input": 0.3, "output": 0.3},
    "meta-llama/llama-3.2-1b-instruct:free": {"input": 0, "output": 0},
    "meta-llama/llama-3.2-3b-instruct:free": {"input": 0.06, "output": 0.06},
    "qwen/qwen-2.5-72b-instruct:free": {"input": 1.2, "output": 1.2},
    "meta-llama/llama-3.1-8b-instruct:free": {"input": 0.18, "output": 0.18},
    "google/gemma-2-9b-it:free": {"input": 0.3, "output": 0.3},
    "mistralai/mistral-7b-instruct:free": {"input": 0.2, "output": 0.2},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3-5-haiku-20241022": {"input": 0.8, "output": 4.00},
}

MODEL_TO_PROVIDER_MAP = {
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": "together",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": "together",
    "deepseek-ai/DeepSeek-V3": "together",
    "Qwen/Qwen2.5-7B-Instruct-Turbo": "together",
    "Qwen/QwQ-32B": "together",
    "mistralai/Mistral-7B-Instruct-v0.3": "together",
    "mistralai/Mistral-Small-24B-Instruct-2501": "together",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": "together",
    "meta-llama/Llama-3.2-3B-Instruct-Turbo": "together",
    "google/gemma-2-9b-it": "together",
    "google/gemma-2-27b-it": "together",
    "gemini-2.0-flash": "google",
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "deepseek/deepseek-chat-v3-0324:free": "openrouter",
    "meta-llama/llama-4-maverick:free": "openrouter",    # english centric
    "meta-llama/llama-4-scout:free": "openrouter",       # english centric
    "google/gemini-2.5-pro-exp-03-25:free": "openrouter",
    "mistralai/mistral-small-3.1-24b-instruct:free": "openrouter",
    "google/gemma-3-1b-it:free": "openrouter",
    "google/gemma-3-4b-it:free": "openrouter",
    "google/gemma-3-12b-it:free": "openrouter",
    "google/gemma-3-27b-it:free": "openrouter",
    "deepseek/deepseek-r1-zero:free": "openrouter",
    "qwen/qwq-32b:free": "openrouter",
    "google/gemini-2.0-pro-exp-02-05:free": "openrouter",  # problem
    "deepseek/deepseek-r1:free": "openrouter",
    "deepseek/deepseek-chat:free": "openrouter",
    "meta-llama/llama-3.3-70b-instruct:free": "openrouter",
    "qwen/qwen-2.5-7b-instruct:free": "openrouter",
    "meta-llama/llama-3.2-1b-instruct:free": "openrouter",
    "meta-llama/llama-3.2-3b-instruct:free": "openrouter",
    "qwen/qwen-2.5-72b-instruct:free": "openrouter",
    "meta-llama/llama-3.1-8b-instruct:free": "openrouter",
    "google/gemma-2-9b-it:free": "openrouter",
    "mistralai/mistral-7b-instruct:free": "openrouter",
    "claude-3-haiku-20240307": "anthropic",
    "claude-3-5-haiku-20241022": "anthropic",
}


MODEL_TO_CORE_MAP = {
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": "meta-llama-3.1-405b-instruct",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": "meta-llama-3.3-70b-instruct",
    "deepseek-ai/DeepSeek-V3": "deepseek-v3",
    "Qwen/Qwen2.5-7B-Instruct-Turbo": "qwen-2.5-7b-instruct",
    "Qwen/QwQ-32B": "qwq-32b",
    "mistralai/Mistral-7B-Instruct-v0.3": "mistral-7b-instruct",
    "mistralai/Mistral-Small-24B-Instruct-2501": "mistral-small-3.1-24b-instruct",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": "meta-llama-3.1-8b-instruct",
    "meta-llama/Llama-3.2-3B-Instruct-Turbo": "meta-llama-3.2-3b-instruct",
    "google/gemma-2-9b-it": "gemma-2-9b-it",
    "google/gemma-2-27b-it": "gemma-2-27b-it",
    "gemini-2.0-flash": "gemini-2.0-flash",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "deepseek/deepseek-chat-v3-0324:free": "deepseek-v3",
    "meta-llama/llama-4-maverick:free": "meta-llama-4-maverick",
    "meta-llama/llama-4-scout:free": "meta-llama-4-scout",
    "google/gemini-2.5-pro-exp-03-25:free": "gemini-2.5-pro",
    "mistralai/mistral-small-3.1-24b-instruct:free": "mistral-small-3.1-24b-instruct",
    "google/gemma-3-1b-it:free": "gemma-3-1b-it",
    "google/gemma-3-4b-it:free": "gemma-3-4b-it",
    "google/gemma-3-12b-it:free": "gemma-3-12b-it",
    "google/gemma-3-27b-it:free": "gemma-3-27b-it",
    "deepseek/deepseek-r1-zero:free": "deepseek-r1-zero",
    "qwen/qwq-32b:free": "qwq-32b",
    "google/gemini-2.0-pro-exp-02-05:free": "gemini-2.0-pro",
    "deepseek/deepseek-r1:free": "deepseek-r1",
    "deepseek/deepseek-chat:free": "deepseek-v3",
    "meta-llama/llama-3.3-70b-instruct:free": "meta-llama-3.3-70b-instruct",
    "qwen/qwen-2.5-7b-instruct:free": "qwen-2.5-7b-instruct",
    "meta-llama/llama-3.2-1b-instruct:free": "meta-llama-3.2-1b-instruct",
    "meta-llama/llama-3.2-3b-instruct:free": "meta-llama-3.2-3b-instruct",
    "qwen/qwen-2.5-72b-instruct:free": "qwen-2.5-72b-instruct",
    "meta-llama/llama-3.1-8b-instruct:free": "meta-llama-3.1-8b-instruct",
    "google/gemma-2-9b-it:free": "gemma-2-9b-it",
    "mistralai/mistral-7b-instruct:free": "mistral-7b-instruct",
    "claude-3-haiku-20240307": "claude-3-haiku",
    "claude-3-5-haiku-20241022": "claude-3.5-haiku",
}


# singleton
from typing import Dict, Optional

class LLMClient:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LLMClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model: str = "gpt-4o-mini", api_keys: Optional[Dict[str, list]] = None, max_retries: int = 5):
        """
        Initialize the client with a model, optional API keys, and max retries.
        
        Args:
            model (str): Model name from MODEL_TO_PROVIDER_MAP. Defaults to "gpt-4o-mini".
            api_keys (Dict[str, list]): Dictionary of provider: [keys] (e.g., {"openai": ["key1", "key2"]}).
                If None, keys are collected from environment variables.
            max_retries (int): Maximum number of retries for failed API calls. Defaults to 5.
        """
        if not self._initialized:
            self.api_keys = api_keys or self._collect_api_keys()
            self.max_retries = max_retries

            self.calls_so_far = 0
            self.input_tokens_so_far = 0
            self.output_tokens_so_far = 0
            self.cost_so_far = 0

            self.set_model(model)
            self._initialized = True

    def init_counts_to_zero(self):
        self.calls_so_far = 0
        self.input_tokens_so_far = 0
        self.output_tokens_so_far = 0
        self.cost_so_far = 0

    def _collect_api_keys(self) -> Dict[str, list]:
        """Collect API keys from environment variables."""
        api_keys = {}
        for key_name, value in os.environ.items():
            if "_API_KEY" in key_name and value:
                provider = key_name.split("_API_KEY")[0].lower()
                if provider in api_keys:
                    api_keys[provider].append(value)
                else:
                    api_keys[provider] = [value]
        return api_keys
    
    def _extract_json_block(self, s: str) -> str:
        start = s.find("```json")
        if start == -1:
            start = s.find("```")  # Fallback to plain code block
        end = s.find("```", start + 7 if "json" in s[start:start+7] else start + 3)
        if start != -1 and end != -1:
            return s[start + (7 if "json" in s[start:start+7] else 3):end].strip()
        if start != -1 and end == -1:
            raise ValueError("Unclosed JSON block")
        return s

    def _parse_json_from_output(self, text):
        json_text = self._extract_json_block(text)
        
        # Remove control characters
        json_text = re.sub(r'[\x00-\x1F\x7F]', '', json_text)
        # Remove invalid escape sequences
        json_text = re.sub(r'\\(?!["\\/bfnrtu])', '', json_text)
        json_text = re.sub(r'\\u[0-9A-Fa-f]{0,3}(?![0-9A-Fa-f])', '', json_text)
        
        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
    
    # def _get_client(self, provider, model, api_key):
    #     client = None
    #     if provider == "together":
    #         client = ChatTogether(model=model, api_key=api_key)
    #     elif provider == "google":
    #         client = ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
    #     elif provider == "openai":
    #         client = ChatOpenAI(model=model, api_key=api_key)
    #     elif provider == "openrouter":
    #         client = ChatOpenAI(
    #             model=model,
    #             api_key=api_key,
    #             openai_api_base="https://openrouter.ai/api/v1"
    #         )
    #     else:
    #         raise ValueError(f"Unsupported provider: {provider}")
    #     return client
    
    # def _get_client(self, provider, model, api_key, max_retries=0, retry_delay=1.0, temperature=0.7, max_tokens=None):
    #     client = None
    #     base_config = {
    #         "model": model,
    #         "api_key": api_key,
    #         "max_retries": max_retries,
    #         # "retry_delay": retry_delay,  # in seconds
    #         # "temperature": temperature,
    #         # "max_tokens": max_tokens,
    #     }
        
    #     if provider == "together":
    #         client = ChatTogether(**base_config)
    #     elif provider == "google":
    #         client = ChatGoogleGenerativeAI(
    #             **base_config,
    #             google_api_key=api_key  # Google might need this named differently
    #         )
    #     elif provider == "openai":
    #         client = ChatOpenAI(**base_config)
    #     elif provider == "openrouter":
    #         client = ChatOpenAI(
    #             **base_config,
    #             openai_api_base="https://openrouter.ai/api/v1"
    #         )
    #     else:
    #         raise ValueError(f"Unsupported provider: {provider}")
        
    #     return client

    def _get_client(self, provider, model, api_key, max_retries=0, retry_delay=1.0, temperature=0.7, max_tokens=None):
        client = None
        base_config = {
            "model": model,
            "api_key": api_key,
            "max_retries": max_retries,
            # "retry_delay": retry_delay,  # in seconds
            # "temperature": temperature,
            # "max_tokens": max_tokens,
        }
        
        if provider == "together":
            client = ChatTogether(**base_config)
        elif provider == "google":
            client = ChatGoogleGenerativeAI(
                **base_config,
                google_api_key=api_key  # Google might need this named differently
            )
        elif provider == "openai":
            client = ChatOpenAI(**base_config)
        elif provider == "openrouter":
            client = ChatOpenAI(
                **base_config,
                openai_api_base="https://openrouter.ai/api/v1"
            )
        elif provider == "anthropic":
            client = ChatAnthropic(**base_config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return client

    def set_model(self, model: str) -> None:
        """
        Change the model and reinitialize the client accordingly.
        
        Args:
            model (str): New model name from MODEL_TO_PROVIDER_MAP
        """
        self.model = model
        self.provider = MODEL_TO_PROVIDER_MAP.get(model, "openai")
        
        available_keys = self.api_keys.get(self.provider.lower(), [])
        if not available_keys:
            self.client = None
            return
        
        key = random.choice(available_keys)
        self.client = self._get_client(self.provider, model, key)

    def _get_api_key(self, provider: str, used_keys: set) -> str:
        # for now ignore this bookkeeping
        used_keys = {}

        """Retrieve a random available API key that hasn't been used yet."""
        available_keys = [key for key in self.api_keys.get(provider.lower(), []) if key not in used_keys]
        if not available_keys:
            return None
        return random.choice(available_keys)
    
    def _convert_to_langchain_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """Convert dict messages to LangChain message objects."""
        langchain_messages = []
        for message in messages:
            if message["role"] == "system":
                langchain_messages.append(SystemMessage(content=message["content"]))
            elif message["role"] == "user":
                langchain_messages.append(HumanMessage(content=message["content"]))
            elif message["role"] == "assistant":
                langchain_messages.append(AIMessage(content=message["content"]))
        return langchain_messages
    
    def get_embedding(self, text: str, model: str = DEFAULT_OPENAI_EMBEDDING_MODEL) -> list:
        """Get embeddings for the given text using an OpenAI model."""
        active_provider = "openai"
        api_key = self._get_api_key(active_provider, set())
        if not api_key:
            raise ValueError("Error: No valid OpenAI API key available.")
        temp_client = OpenAI(api_key=api_key)
        return temp_client.embeddings.create(input = [text], model=model).data[0].embedding

    def get_chat_completion(self, messages: List[Dict[str, str]], model_name: str = None) -> str:
        """
        Get a response from the model using a list of messages with retry logic.
        
        Args:
            messages (List[Dict[str, str]]): List of message dictionaries with 'role' and 'content' keys
            model (str, optional): Model to use for this response; defaults to the client's current model
        
        Returns:
            str: Model's response
        """
        self.calls_so_far += 1
        active_model = model_name if model_name else self.model
        active_provider = MODEL_TO_PROVIDER_MAP.get(active_model, "openai")

        available_keys = self.api_keys.get(active_provider.lower(), [])
        if not available_keys:
            error_message = f"Error: No valid API key provided for {active_provider}."
            raise Exception(error_message)
        
        retries = 0
        used_keys = set()

        print(f"\n\nget_chat_completion: provider = {active_provider}, model = {active_model}\n\n")

        while retries < self.max_retries:
            api_key = self._get_api_key(active_provider, used_keys)

            # print(f"\nusing api key = {api_key} \n\n")

            if not api_key:
                error_message = f"Error: All API keys for {active_provider} have been tried and failed."
                raise Exception(error_message)
            
            used_keys.add(api_key)
            retries += 1

            try:
                temp_client = self._get_client(active_provider, active_model, api_key)

                # Convert messages to LangChain format if needed
                langchain_messages = self._convert_to_langchain_messages(messages)
                
                import time
                # Record start time
                start_time = time.perf_counter()

                # Get response
                response = temp_client.invoke(langchain_messages)

                end_time = time.perf_counter()
                inference_time = end_time - start_time


                message = response.content

                input_tokens = response.usage_metadata['input_tokens']
                output_tokens = response.usage_metadata['output_tokens']
                total_cost = 0

                # Calculate cost
                if active_model in MODEL_COST_PER_MILLION:
                    input_cost = (input_tokens / 1_000_000) * MODEL_COST_PER_MILLION[active_model]["input"]
                    output_cost = (output_tokens / 1_000_000) * MODEL_COST_PER_MILLION[active_model]["output"]
                    total_cost = input_cost + output_cost

                # Update properties inside class
                self.input_tokens_so_far += input_tokens
                self.output_tokens_so_far += output_tokens
                self.cost_so_far += total_cost

                try:
                    parsed_json = self._parse_json_from_output(message)
                except Exception:
                    parsed_json = None
            
                return {
                    "output_text": message,
                    "parsed_json": parsed_json,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "total_cost": total_cost,
                    "provider": active_provider,
                    "model": active_model,
                    "inference_time": inference_time
                }

            except Exception as e:
                if retries == self.max_retries:
                    error_message = f"Error: Max retries ({self.max_retries}) reached for {active_provider}. Last error: {str(e)}"
                    raise Exception(error_message)
                
                time.sleep(60)
                
                continue

    def get_response(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model_name: str = None) -> str:
        """
        Get a response from the model with random key shuffling and retry logic.
        
        Args:
            prompt (str): User input prompt
            system_prompt (str): System prompt to set context
            model (str, optional): Model to use for this response; defaults to the client's current model
        
        Returns:
            str: Model's response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        chat_completion = self.get_chat_completion(messages, model_name)

        response = {"input_text": prompt}
        response.update(chat_completion)

        return response

    def get_stats(self) -> Dict[str, Any]:
        """Return usage statistics."""
        return {
            "calls": self.calls_so_far,
            "input_tokens": self.input_tokens_so_far,
            "output_tokens": self.output_tokens_so_far,
            "cost": self.cost_so_far
        }


# Example usage:
if __name__ == "__main__":
    # API keys should be set in environment variables or passed explicitly
    client = LLMClient(model="gpt-4o-mini", max_retries=3)
    
    # Using single prompt
    response = client.get_response("Hello, how are you?")
    print("Initial response (gpt-4o-mini):", response)
    
    # Using chat messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me about Python."},
        {"role": "assistant", "content": "Python is a high-level programming language."},
        {"role": "user", "content": "How is it used in data science?"}
    ]
    response = client.get_chat_completion(messages)
    print("Chat completion response:", response)

    # Switching models
    client.set_model("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")
    response = client.get_response("What's the weather like?")
    print("New response (Llama-3.3-70B):", response)

    print("Stats:", client.get_stats())