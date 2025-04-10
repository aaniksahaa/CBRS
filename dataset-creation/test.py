from llmclients import *
from util import *

client = LLMClient()

model = "meta-llama/llama-3.2-3b-instruct:free"
# model = "deepseek/deepseek-chat:free"
# model = "meta-llama/llama-3.1-8b-instruct:free"
model = "mistralai/Mistral-7B-Instruct-v0.3"
model = "claude-3-haiku-20240307"
model = "claude-3-5-haiku-20241022"

client.set_model(model)

test_messages = [
    "hello, how you doing?",
    "তুমি কেমন আছ?"
]

for i, m in enumerate(test_messages):
    response = client.get_response(m)
    print(response)
    write_json(f"out/out_{i+1}.json", response)