from llmclients import *
from util import *

client = LLMClient()

client.set_model("deepseek/deepseek-chat:free")
# client.set_model("meta-llama/llama-3.1-8b-instruct:free")

test_messages = [
    "hello, how you doing?",
    "তুমি কেমন আছ?"
]

for i, m in enumerate(test_messages):
    response = client.get_response(m)
    print(response)
    write_json(f"out_{i+1}.json", response)