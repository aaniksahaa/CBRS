from parser import *
from util import *

msg = "Jannatu Nayem Evan এর জন্য ইমার্জেন্সি O+ blood লাগবে\n\nEmergency 10 bag o+ blood lagbe \nOnk serious obostha amar friend er \n\nBlood group : O+ \n\nAmount : 10 bag\n\nHospital : Ever care hospital \n\nLocation : Boshudhoara \n\nPlease help.  Its urgent \n\nMobile : 01719337179\n\nContact Jawad Zahin bhaiya or call"

provider = 'together'

model = 'deepseek-ai/DeepSeek-V3'
model = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'

provider = 'openai'
model = 'gpt-4o-mini'

out = parse_blood_donation_request_text(msg, provider=provider, model=model)

write_json('out.json', out)