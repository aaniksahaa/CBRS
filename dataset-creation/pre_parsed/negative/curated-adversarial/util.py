import os
import re 
import json
import random
import logging
from typing import List, Dict, Any
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from together import Together
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage

# Setup
dotenv_path = os.getenv("DOTENV_PATH", ".env")
load_dotenv(dotenv_path)

logging.basicConfig(
    filename='api_key_usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Config
SUPPORTED_PROVIDERS = ["together", "google", "openai"]
DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
DEFAULT_MAX_RETRIES = 5

MODEL_COST_PER_MILLION = {
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": {
        "input": 3.5,
        "output": 3.5
    },
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": {
        "input": 0.88,
        "output": 0.88
    },
    "deepseek-ai/DeepSeek-V3": {
        "input": 1.25,
        "output": 1.25
    },
    "Qwen/Qwen2.5-7B-Instruct-Turbo": {
        "input": 0.3,
        "output": 0.3
    },
    "mistralai/Mistral-7B-Instruct-v0.3": {
        "input": 0.2,
        "output": 0.2
    },
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": {
        "input": 0.18,
        "output": 0.18
    },
    "google/gemma-2-9b-it": {
        "input": 0.3,
        "output": 0.3
    },
    "google/gemma-2-27b-it": {
        "input": 0.8,
        "output": 0.8
    },
    "gemini-2.0-flash": {
        "input": 0.1,
        "output": 0.4
    }
}

def get_cost(model, input_tokens, output_tokens):
    if model not in MODEL_COST_PER_MILLION:
        return 0
        
    input_cost = (input_tokens / 1_000_000) * MODEL_COST_PER_MILLION[model]["input"]
    output_cost = (output_tokens / 1_000_000) * MODEL_COST_PER_MILLION[model]["output"]
    
    return input_cost + output_cost

def collect_api_keys() -> dict:
    api_keys = {}
    for provider in SUPPORTED_PROVIDERS:
        keys = []
        # Get all environment variables
        env_vars = os.environ
        # Filter for variables that start with the provider's name followed by "_API_KEY"
        provider_prefix = f"{provider.upper()}_API_KEY"
        for key_name, key_value in env_vars.items():
            if key_name.startswith(provider_prefix) and key_value:
                keys.append(key_value)
        api_keys[provider] = keys
    return api_keys

def show_api_key_stats(api_keys: dict) -> None:
    """
    Display statistics about the collected API keys for each provider.
    
    Args:
        api_keys (dict): Dictionary mapping providers to their list of API keys.
    """
    print("API Key Statistics:")
    print("-" * 40)
    
    total_keys = 0
    for provider in SUPPORTED_PROVIDERS:
        key_count = len(api_keys.get(provider, []))
        total_keys += key_count
        
        # Get the actual key names from environment variables for this provider
        provider_prefix = f"{provider.upper()}_API_KEY"
        key_names = [
            key_name for key_name in os.environ.keys() 
            if key_name.startswith(provider_prefix) and os.environ[key_name]
        ]
        
        print(f"Provider: {provider.capitalize()}")
        print(f"  Number of API Keys: {key_count}")
        if key_count > 0:
            print("  Key Names:")
            for name in key_names:
                # Mask the actual key value for security, showing only first 3 and last 3 characters
                key_value = os.environ[name]
                masked_key = f"{key_value[:3]}...{key_value[-3:]}" if len(key_value) > 6 else key_value
                print(f"    - {name}: {masked_key}")
        else:
            print("  (No API keys found)")
        print()
    
    print("-" * 40)
    print(f"Total API Keys Across All Providers: {total_keys}")

API_KEYS = collect_api_keys()

# show_api_key_stats(API_KEYS)
# exit(0)

def get_response(prompt: str, provider: str, model: str = DEFAULT_MODEL, max_retries: int = DEFAULT_MAX_RETRIES) -> dict:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'. Must be one of {SUPPORTED_PROVIDERS}.")

    if not API_KEYS.get(provider):
        raise ValueError(f"No API keys found for provider '{provider}'.")

    retries = 0
    used_keys = set()

    while retries < max_retries:
        available_keys = [key for key in API_KEYS[provider] if key not in used_keys]
        if not available_keys:
            raise Exception(f"All API keys for '{provider}' have been tried and failed.")

        api_key = random.choice(available_keys)
        used_keys.add(api_key)

        try:
            if provider == "together":
                client = Together(api_key=api_key)
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    # temperature=0.2
                )
                message = response.choices[0].message.content
                usage = response.usage

                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                total_tokens = usage.total_tokens if usage else 0
                total_cost = get_cost(model, input_tokens, output_tokens)

            elif provider == "google":
                chat = ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.2)
                response = chat.invoke([HumanMessage(content=prompt)])
                message = response.content

                usage = getattr(response, "usage_metadata", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)
                total_cost = get_cost(model, input_tokens, output_tokens)

            elif provider == "openai":
                chat = ChatOpenAI(model=model, openai_api_key=api_key, temperature=0.2)
                with get_openai_callback() as cb:
                    response = chat.invoke([HumanMessage(content=prompt)])
                    message = response.content

                    usage = getattr(response, "usage_metadata", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    total_tokens = usage.get("total_tokens", 0)
                    total_cost = cb.total_cost

            return {
                "input_text": prompt,
                "output_text": message,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "provider": provider,
                "model": model
            }

        except Exception as e:
            retries += 1
            key_index = API_KEYS[provider].index(api_key)
            key_name = f"{provider.upper()}_API_KEY_{key_index + 1}" if key_index > 0 else f"{provider.upper()}_API_KEY"

            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                logging.info(f"{key_name} likely exceeded rate/quota: {str(e)}")
            else:
                logging.error(f"Error with {provider} key {key_name} (attempt {retries}/{max_retries}): {str(e)}")

            if retries == max_retries:
                raise Exception(f"Max retries ({max_retries}) reached for {provider}. Last error: {str(e)}")


import json

def extract_json_block(s: str) -> str:
    start = s.find("```json")
    if start == -1:
        start = s.find("```")  # Fallback to plain code block
    end = s.find("```", start + 7 if "json" in s[start:start+7] else start + 3)
    if start != -1 and end != -1:
        return s[start + (7 if "json" in s[start:start+7] else 3):end].strip()
    if start != -1 and end == -1:
        raise ValueError("Unclosed JSON block")
    return s

def parse_json_from_output(text):
    json_text = extract_json_block(text)
    
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

def read_txt(path):
    """Reads a text file and returns its contents as a string."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_txt(path, content):
    """Writes a string to a text file."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_json(path):
    """Reads a JSON file and returns the parsed object (dict or list)."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, obj):
    """Serializes a Python object to a JSON file with indentation and Unicode support."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

