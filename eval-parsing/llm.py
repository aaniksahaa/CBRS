import os
import random
import logging
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from together import Together
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
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
MAX_RETRIES = 3

MODEL_PRICING_PER_MILLION = {
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": 0.88,
    "deepseek-ai/DeepSeek-V3": 1.25,
    "Qwen/Qwen2.5-7B-Instruct-Turbo": 0.3,
    "mistralai/Mistral-7B-Instruct-v0.3": 0.2,
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": 0.18,
    "google/gemma-2-9b-it": 0.3,
    "google/gemma-2-27b-it": 0.8
}

# Collect API keys by provider
def collect_api_keys() -> dict:
    api_keys = {}
    for provider in SUPPORTED_PROVIDERS:
        keys = []
        i = 1
        while True:
            key_name = f"{provider.upper()}_API_KEY_{i}"
            key = os.getenv(key_name)
            if not key:
                if i == 1:
                    base_key = os.getenv(f"{provider.upper()}_API_KEY")
                    if base_key:
                        keys.append(base_key)
                break
            keys.append(key)
            i += 1
        api_keys[provider] = keys
    return api_keys

API_KEYS = collect_api_keys()

# Unified function
def call_model(prompt: str, provider: str, model: str = DEFAULT_MODEL) -> Tuple[str, Optional[int], Optional[int], Optional[int], Optional[float]]:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(f"Unsupported provider '{provider}'. Must be one of {SUPPORTED_PROVIDERS}.")

    if not API_KEYS.get(provider):
        raise ValueError(f"No API keys found for provider '{provider}'.")

    retries = 0
    used_keys = set()

    while retries < MAX_RETRIES:
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
                    temperature=0.2
                )
                message = response.choices[0].message.content
                usage = response.usage

                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                total_tokens = usage.total_tokens if usage else 0

                cost_per_token = MODEL_PRICING_PER_MILLION.get(model, 1.0) / 1_000_000
                total_cost = total_tokens * cost_per_token

                return message, input_tokens, output_tokens, total_tokens, total_cost

            elif provider == "google":
                chat = ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.2)
                response = chat.invoke([HumanMessage(content=prompt)])
                return response.content, None, None, None, None

            elif provider == "openai":
                chat = ChatOpenAI(model=model, openai_api_key=api_key, temperature=0.2)
                response = chat.invoke([HumanMessage(content=prompt)])
                return response.content, None, None, None, None

        except Exception as e:
            retries += 1
            key_index = API_KEYS[provider].index(api_key)
            key_name = f"{provider.upper()}_API_KEY_{key_index + 1}" if key_index > 0 else f"{provider.upper()}_API_KEY"

            if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                logging.info(f"{key_name} likely exceeded rate/quota: {str(e)}")
            else:
                logging.error(f"Error with {provider} key {key_name} (attempt {retries}/{MAX_RETRIES}): {str(e)}")

            if retries == MAX_RETRIES:
                raise Exception(f"Max retries ({MAX_RETRIES}) reached for {provider}. Last error: {str(e)}")
