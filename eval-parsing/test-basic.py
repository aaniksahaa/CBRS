from util import *

text = 'hello, how you?'

provider = 'openai'
model = 'gpt-4o-mini'

# print(call_model(text, provider='together', model='meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'))

print(call_model(text, provider='google', model='gemini-2.0-flash'))

# print(call_model(text, provider='openai', model='gpt-4o-mini'))
