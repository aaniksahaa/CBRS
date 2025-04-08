from parser import *
from util import *

msg = "jatayater vara deya hobe, Jannatu Nayem Evan এর জন্য ইমার্জেন্সি O+ blood লাগবে\n\nEmergency 10 bag o+ blood lagbe \nOnk serious obostha amar friend er \n\nBlood group : O+ \n\nAmount : 10 bag\n\nHospital : Ever care hospital \n\nLocation : Boshudhoara \n\nPlease help.  Its urgent \n\nMobile : 01719337179\n\nContact Jawad Zahin bhaiya or call"

msg = """
ব্লাড ক্যান্সার আক্রান্ত একজন ভাইয়ের জন্য আজ 
09-07-2024 তারিখে সকাল ৯টা থেকে ১১টার মধ্যে ১ ব্যাগ 
"বি পজেটিভ" রক্ত দরকার। 
স্থানঃ রাজশাহী মেডিকেল হাসপাতাল, রাজশাহী 
ফোনঃ- 01721207XYZ (রোগীর ভাই)
যাতায়াতের ভাড়া দিয়ে দেওয়া হবে।
"""

# msg = """
# Emergency Blood Needed
# Time: Tomorrow at 10pm
# BG: A+
# Location : Dhanmondi popular Hospital, Dhaka
# Transport cost will not be provided.
# Please knock me if anyone is available
# """

msg = """
Emergency 4-5 bag O negative blood dorkar choto bacchar jonno, bacchar nam Mahin
Location: Rangpur doctors hospital
Time : 2 Aug sokal 10tar age
Can anyone help me please?
ami Antika, amake jogajog korben plz othoba Muhib (01556-789XXX)
asha jaowar vara diye deowa hobe
"""

# msg = "hello, how are you?"

provider = 'together'
model = 'deepseek-ai/DeepSeek-V3'
model = 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free'

provider = 'google'
model='gemini-2.0-flash'

# provider = 'openai'
# model = 'gpt-4o-mini'

# method = "zero_shot"
method = "few_shot"

metadata = {
    "language": "bn"
}

write_txt('prompt.txt', build_few_shot_prompt(msg))
# exit(0)

out = parse_blood_donation_request(msg, provider=provider, model=model, method=method, metadata=metadata)

write_json('out.json', out)