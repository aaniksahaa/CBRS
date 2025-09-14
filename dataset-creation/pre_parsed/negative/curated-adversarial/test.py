from llmclient import *
from util import *

client = LLMClient()

# client.set_model("gemini-2.0-flash")
client.set_model("gpt-4o-mini")
# client.set_model("meta-llama/llama-3.1-8b-instruct:free")

test_messages = [
    "hello, how you doing?, give the response in exact json format, with key 'status' and value ok or not ok.",
    "তুমি কেমন আছ?"
]

os.makedirs("out", exist_ok=True)

for i, m in enumerate(test_messages):
    response = client.get_response(m)
    print(response)
    write_json(f"out/out_{i+1}.json", response)