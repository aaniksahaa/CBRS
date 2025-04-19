from util import *

text = 'hello, how you?'

provider='together'
model='meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'

provider = 'google'
model='gemini-2.0-flash'

provider = 'openai'
model = 'gpt-4o-mini'

print(get_response(text, provider=provider, model=model))
