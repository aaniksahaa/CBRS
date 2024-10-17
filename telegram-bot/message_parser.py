from utils import * 

def parse_int(s):
    try:
        return int(s)
    except Exception:
        return None 

# making db ready
def get_modified_data(d):
    patient = d.get('patient', None)
    compensation = d.get('compensation', None)
    contacts = d.get('contacts', [])

    modified_contacts = []

    for c in contacts:
        modified_contacts.append({
            "name": c.get('name', ''),
            "numbers": c.get('contact_numbers', []),
            "relationWithPatient": c.get("relation_with_patient", '')
        })

    data = {
            "messageText": "",
            "bloodGroup": d.get('blood_group', ''),
            "bagsNeeded": parse_int(d.get('bags_needed', '')),
            "patientName": patient.get('name', '') if patient else '',
            "patientGender": patient.get('gender', '') if patient else '',
            "patientAgeGroup": patient.get('age_group', '') if patient else '',
            "condition": d.get('condition', ''),
            "location": d.get('location', ''),
            "hospitalName": d.get('hospital_name', ''),
            "locationMarkers": d.get('location_markers', []),
            "probableDay": d.get('probable_day', ''),
            "probableTime": d.get('probable_time', ''),
            "transportation": compensation.get('transportation', '') if compensation else '',
            "allowance": compensation.get('allowance', '') if compensation else '',
            "contacts": modified_contacts
        }
    
    return data 


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
    "is_seeking_blood_donation": "true",
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
    "is_seeking_blood_donation": "true",
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
    "is_seeking_blood_donation": "true",
    "blood_group": "A+",
    "bags_needed": "1",
    "patient": {
        "name":"",
        "gender": "",
        "age-group":"teenager"
    },
    "condition": "Stone operation",
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

sample_negative_inp = """
How are you! Blood is very important for our life. Donating blood is good for health.
"""

sample_negative_out = {
    "is_seeking_blood_donation": "false"
}


def parse_blood_seeking_message(user_text):
    prompt = PromptTemplate(
        template="""
You will be given a text message from a sender that is most possibly a blood donation seeking message.
If not, then just output that it is not seeking blood donation.
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
{sample_out_1}

Text Message:
{sample_inp_2}
Your reponse json:
{sample_out_2}

Text Message:
{sample_negative_inp}
Your reponse json:
{sample_negative_out}

Now output the correctly formatted json for the following Text Message:

{user_text}

Reminders:
- Following the exact json format as example is mandatory
- Do not use any greetings etc. You must output ONLY the required correctly formatted json, nothing else
- Do not hallucinate. If you think, a piece of information is not present, keep that an empty string

    """,
        input_variables=["sample_inp_1", "sample_out_1", "sample_inp_1", "sample_out_1", "user_text"]
    )

    chain = prompt | llm 

    with get_openai_callback() as cb:
        # place_name = "Uttara 11, Mansur Ali Medical College"
        response = chain.invoke({
            "sample_inp_1": sample_inp_1,
            "sample_out_1": json.dumps(sample_out_1),
            "sample_inp_2": sample_inp_2,
            "sample_out_2": json.dumps(sample_out_2),
            "sample_negative_inp": sample_negative_inp,
            "sample_negative_out": json.dumps(sample_negative_out),
            "user_text": user_text
        })
        print(cb)
    
    message = response.content

    data = message.replace('```','').replace('json','')

    data = re.sub(r'\\u[0-9a-fA-F]{0,3}[^0-9a-fA-F]', '', data)

    try:
        data = json.loads(data)
    except Exception as e:
        print(f"An unexpected error occurred while parsing json: {e}")
        data = {'error': True}
        return data
    
    print(data)

    if data.get("is_seeking_blood_donation", "true").lower() == "false":
        data = {'error': True}
        return data

    data = get_modified_data(data)

    totalLocation = data['hospitalName'] + " in " + data["location"]
    coords = get_coordinates(totalLocation)

    data['latitude'] = coords.get('latitude', None)
    data['longitude'] = coords.get('longitude', None)

    data['messageText'] = user_text

    return data

if __name__ == "__main__":
    test_message = """
    জরুরি ভিত্তিতে  B-  রক্তের প্রয়োজন। 

    🔴রক্তের গ্রুপঃ B- 

    💉রক্তের পরিমাণঃ 1 ব্যাগ 
    রক্ত দানের সময় : ২৪-০৫-২০২৪ তারিখের মধ্যে 
    রোগীর সমস্যা : Burn 

    হসপিটাল: Shaikh hasina burn unit 

    যোগাযোগ: +880 1816-203394( রোগীর স্বামী), 01617-782064 ( রোগীর আত্মীয় )
    """

    # test_message = "hi"

    data = parse_blood_seeking_message(test_message)

    print(data)