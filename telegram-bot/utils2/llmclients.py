from openai import OpenAI
from .constants import * 
from .misc import debug
import tiktoken
import os
import time

load_dotenv()

prices = {
    'gpt-3.5-turbo': {
        'input_pricing': 1.5,
        'output_pricing': 2
    },
    'gpt-4o': {
        'input_pricing': 5,
        'output_pricing': 15
    },
    'gpt-4o-mini': {
        'input_pricing': 0.15,
        'output_pricing': 0.6
    },
}

def count_tokens(text, model_name=DEFAULT_OPENAI_CHAT_MODEL):
    encoder = tiktoken.encoding_for_model(model_name)
    tokens = encoder.encode(text)
    return len(tokens)

def count_convo_tokens(messages,model_name=DEFAULT_OPENAI_CHAT_MODEL):
    ans = 0
    for m in messages:
        ans += count_tokens(m['content'],model_name)
    return ans

def get_price(input_tokens, output_tokens, model_name):
    pricing = prices.get(model_name,None)
    if(not pricing):
       return 0
    price = (input_tokens*pricing['input_pricing'] + output_tokens*pricing['output_pricing'])/(10**(6))
    return round(price,8)

class OpenAIClient:
    _instance = None
    calls = 0
    input_token = 0
    output_token = 0
    cost = 0
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))
    def get_calls(self):
        return self.calls
    def get_openai_embedding(self, text, model):
      return self.client.embeddings.create(input = [text], model=model).data[0].embedding
    def get_chat_completion(self, messages, model_name=DEFAULT_OPENAI_CHAT_MODEL):
        if not messages:
            return ''
        response = self.client.chat.completions.create(
          model=model_name,
          messages=messages
        )

        message = response.choices[0].message.content
        usage_info = response.usage
        input_tokens = usage_info.prompt_tokens
        output_tokens = usage_info.completion_tokens

        self.calls += 1
        self.input_token += input_tokens
        self.output_token += output_tokens

        cost = get_price(input_tokens,output_tokens,model_name)

        self.cost += cost

        debug(f"""

Prompt: {messages[-1]['content']}
Response: {message}

Call Details:

Model Name = {model_name}
Input Tokens = {input_tokens}
Output Tokens = {output_tokens}
Cost = {cost} dollars

""")

        return message
    def get_convo_response(self, messages, model_name=DEFAULT_OPENAI_CHAT_MODEL):
        return self.get_chat_completion(messages, model_name)
    def get_response(self, prompt, model_name=DEFAULT_OPENAI_CHAT_MODEL):
        messages=[
          {"role": "system", "content": "You are an assistant."},
          {"role": "user", "content": prompt}
        ]
        return self.get_chat_completion(messages, model_name)
        
        