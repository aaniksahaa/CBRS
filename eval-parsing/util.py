import os
import json
import re
from typing import List, Dict, Any
from together import Together
from dotenv import load_dotenv
import random
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    filename='api_key_usage.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
load_dotenv()

# Config
DEFAULT_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

# Model pricing (per million tokens)
MODEL_PRICING_PER_MILLION = {
    "deepseek-ai/DeepSeek-V3": 1.25,
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": 0.88,
    "google/gemma-2-27b-it": 0.8,
    "Qwen/Qwen2.5-7B-Instruct-Turbo": 0.3,
    "mistralai/Mistral-7B-Instruct-v0.3": 0.2,
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": 0.18,
    "google/gemma-2-9b-it": 0.3
}

# Collect all TOGETHER_API_KEYs from .env
def get_api_keys() -> List[str]:
    api_keys = []
    i = 1
    while True:
        key_name = f"TOGETHER_API_KEY_{i}"
        api_key = os.getenv(key_name)
        if api_key is None:
            # If no more keys are found, break the loop
            if i == 1:
                # Check for the default key if numbered keys aren't found
                default_key = os.getenv("TOGETHER_API_KEY")
                if default_key:
                    api_keys.append(default_key)
                break
            break
        api_keys.append(api_key)
        i += 1
    return api_keys

API_KEYS = get_api_keys()
MAX_RETRIES = 3  # Maximum number of retries for API calls

def call_together(prompt: str, model: str = DEFAULT_MODEL) -> tuple:
    if not API_KEYS:
        raise ValueError("No API keys found in the environment variables.")

    retries = 0
    used_keys = set()  # Track used keys to avoid reusing in the same call

    while retries < MAX_RETRIES:
        # Pick a random API key that hasn't been used yet in this call
        available_keys = [key for key in API_KEYS if key not in used_keys]
        if not available_keys:
            raise Exception("All API keys have been tried and failed.")

        api_key = random.choice(available_keys)
        used_keys.add(api_key)

        try:
            # Initialize Together client with the selected API key
            client = Together(api_key=api_key)
            chat_response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            message = chat_response.choices[0].message.content
            usage = chat_response.usage

            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            total_tokens = usage.total_tokens if usage else 0

            cost_per_token = MODEL_PRICING_PER_MILLION.get(model, 1.0) / 1_000_000
            total_cost = total_tokens * cost_per_token

            return message, input_tokens, output_tokens, total_tokens, total_cost

        except Exception as e:
            retries += 1
            # Check if the error indicates a rate limit or exhausted limit
            if "rate limit" in str(e).lower() or "limit" in str(e).lower():
                key_index = API_KEYS.index(api_key) + 1 if api_key in API_KEYS[1:] else 0
                key_name = f"TOGETHER_API_KEY_{key_index}" if key_index > 0 else "TOGETHER_API_KEY"
                logging.info(f"{key_name} has run out of limit or hit rate limit: {str(e)}")
                # Optionally remove the key from API_KEYS if you want to stop using it entirely
                # API_KEYS.remove(api_key)
            else:
                logging.error(f"Error with API key (attempt {retries}/{MAX_RETRIES}): {str(e)}")

            if retries == MAX_RETRIES:
                raise Exception(f"Max retries ({MAX_RETRIES}) reached. Last error: {str(e)}")

# Example usage
if __name__ == "__main__":
    try:
        response, in_tokens, out_tokens, total_tokens, cost = call_together("Hello, how are you?")
        print(f"Response: {response}")
        print(f"Input Tokens: {in_tokens}, Output Tokens: {out_tokens}, Total Tokens: {total_tokens}, Cost: ${cost:.6f}")
    except Exception as e:
        print(f"Failed to get response: {str(e)}")



import json

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

