import json 
import re 
from .llmclients import *

sample_inp_1 = """
জরুরী ভিত্তিতে  AB(-)রক্তের প্রয়োজন।
আমার ফুপা এর অপারেশন
💁রোগীর সমস্যা: কিডনি সমস্যা
🔴রক্তের গ্রুপ: AB নেগেটিভ
💉রক্তের পরিমাণ: 2 ব্যাগ
📆রক্তদানের তারিখ: 15/02/2024
⌚রক্তদানের সময় : সকাল ৯টা - দুপুর ২টা
🏥রক্তদানের স্থান : কিডনি ফাউন্ডেশন এন্ড রিসার্চ ইনস্টিটিউট, মিরপুর,   ঢাকা।
☎যোগাযোগঃ মার্জান
মোবাইলঃ 01915955585
01928317021
"""

sample_out_1 = {
    "blood_group": "AB-",
    "bags_needed": "2",
    "patient": {
        "name":"",
        "gender": "",
        "age-group":""
    },
    "condition": "Kidney problem, Operation",
    "location": "কিডনি ফাউন্ডেশন এন্ড রিসার্চ ইনস্টিটিউট, মিরপুর,   ঢাকা",
    "hospital_name": "কিডনি ফাউন্ডেশন এন্ড রিসার্চ ইনস্টিটিউট",
    "location_markers": ['মিরপুর', 'ঢাকা'],
    "probable_day": "15/02/2024",
    "probable_time":"09:00-14:00",
    "contacts": [
        {
            "name": "",
            "contact_numbers": [],
            "relation_with_patient": ""
        },
        {
            "name": "মার্জান",
            "contact_numbers": ["01915955585", "01928317021"],
            "relation_with_patient": ""
        },
    ],
    "compensation": {
        "transportation": "",
        "allowance": ""
    }
}

sample_inp_2 = """
Emergency 4-5 bag 0 negative blood dorkar choto bacchar jonno, bacchar nam Mahin
Location: Rangpur doctors hospital 
Time : 2 Aug sokal 10tar age
Can anyone help me please?
ami Antika, amake jogajog korben plz othoba Muhib (01556-789987)
asha jaowar vara diye deowa hobe
"""

sample_out_2 = {
    "blood_group": "O-",
    "bags_needed": "4-5",
    "patient": {
        "name":"Mahin",
        "gender": "",
        "age-group":"child"
    },
    "condition": "",
    "location": "Rangpur doctors hospital",
    "hospital_name": "Rangpur doctors hospital",
    "location_markers": ['Rangpur'],
    "probable_day": "02/08",
    "probable_time":"before 10:00",
    "contacts": [
        {
            "name": "Antika",
            "contact_numbers": [],
            "relation_with_patient": ""
        },
        {
            "name": "Muhib",
            "contact_numbers": ["01556-789987"],
            "relation_with_patient": ""
        }
    ],
    "compensation": {
        "transportation": "Y",
        "allowance": ""
    }
}

sample_inp_3 = """
আসলামু আলাইকুম 
রোগী আমি নিজে - age 17
💂🏼রোগীর সমস্যাঃ পাথর অপারেশন 
🩸রক্তের গ্রুপঃ (A posetive)
💉রক্তের পরিমান:  ১ ব্যাগ
⌚রক্তদানের সময়: আজকেই যত তারাতাড়ি সম্ভব
🏥রক্তদানের স্থানঃ আশা হসপিটাল , রাজশাহী 
☎যোগাযোগ:01741783528
"""

sample_out_3 = {
    "blood_group": "A+",
    "bags_needed": "1",
    "patient": {
        "name":"",
        "gender": "",
        "age-group":"teenager"
    },
    "condition": "Stone peration",
    "location": "আশা হসপিটাল , রাজশাহী",
    "hospital_name": "আশা হসপিটাল , রাজশাহী",
    "location_markers": ['রাজশাহী'],
    "probable_day": "today",
    "probable_time":"now",
    "contacts": [
        {
            "name": "",
            "contact_numbers": ["01741783528"],
            "relation_with_patient": ""
        }
    ],
    "compensation": {
        "transportation": "",
        "allowance": ""
    }
}

sample_inp_4 = """
hello
"""

sample_out_4 = {
    "blood_donation_related": "false"
}

def parse_blood_seeking_message(user_text):
    prompt = f""" 
You will be given a text message from a sender that is most possibly a blood donation seeking message.
If not, then just output that it is not related.
If it is blood donation related, you need to extract information correctly from it in the exact format shown in examples.

You must output a correctly formatted json containing the following fields:

blood_group: must be one of the 8 groups A+ , A- , B+ , B- , O+ , O- , AB+ , AB-
bags_needed: a number in English as a string, like "3" or hyphen-separated two numbers denoting a range like "3-4"
patient: it has three fields name, gender, age_group
        name: the name of patient
        gender: "M" or "F" or ""
        age_group: any of the four :- child / teenager / young / adult
condition: the patient condition in English
location: the stated location exactly as it is in the message
hospital_name: the full name of hospital as stated in the message
location_markers: an array of specific location markers
probable_day: can be in 5 formats, choose as is appropriate according to the message, opt for the more specific date options(DD/MM or DD/MM/YYYY) if you have choices
                DD/MM or DD/MM/YYYY or "today" or "tomorrow" or "n days later"
probable_time: can be in 6 formats, choose as is appropriate according to the message, opt for the more specific time options(HH:MM) if you have choices
                HH:MM or before HH:MM or after HH:MM or HH:MM-HH:MM or "in n hours"
               here you are expected to give the times in 24-hour format
contacts: an array of the contacts you find, each element will be object with 3 fields
            name: the name of person
            contact_numbers: an array of the contact numbers, the numbers should be exact as it is in the message
            relation_with_patient: the relation as stated in message
compensation: will have two fields, they should be either "Y" or "N" or ""
            transportation: whether any compensation for transportation will be provided
            allowance: whether any extra money will be provided

Examples:

Text Message:
{sample_inp_1}
Your reponse json:
{json.dumps(sample_out_1)}

Text Message:
{sample_inp_2}
Your reponse json:
{json.dumps(sample_out_2)}

Text Message:
{sample_inp_3}
Your reponse json:
{json.dumps(sample_out_3)}

Text Message:
{sample_inp_4}
Your reponse json:
{json.dumps(sample_out_4)}

Now output the correctly formatted json for the following Text Message:

{user_text}

Reminders:
- Following the exact json format as example is mandatory
- Do not use any greetings etc. You must output ONLY the required correctly formatted json, nothing else
- Do not hallucinate. If you think, a piece of information is not present, keep that an empty string
    """

    message = OpenAIClient().get_response(prompt)

    data = message.replace('```','').replace('json','')

    data = re.sub(r'\\u[0-9a-fA-F]{0,3}[^0-9a-fA-F]', '', data)

    try:
        data = json.loads(data)
    except Exception as e:
        print(f"An unexpected error occurred while parsing json: {e}")
        data = {'error': 'true'}

    return data