positive_sample_inp_1 = """
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

positive_sample_out_1 = {
    "blood_group": "AB-",
    "bags_needed": "2",
    "patient": {
        "name":"",
        "gender": "",
        "age-group":""
    },
    "condition": "kidney problem, operation",
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

positive_sample_inp_2 = """
Emergency 4-5 bag 0 negative blood dorkar choto bacchar jonno, bacchar nam Mahin
Location: Rangpur doctors hospital 
Time : 2 Aug sokal 10tar age
Can anyone help me please?
ami Antika, amake jogajog korben plz othoba Muhib (01556-789987)
asha jaowar vara diye deowa hobe
"""

positive_sample_out_2 = {
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

positive_sample_inp_3 = """
আসলামু আলাইকুম 
রোগী আমি নিজে - age 17
💂🏼রোগীর সমস্যাঃ পাথর অপারেশন 
🩸রক্তের গ্রুপঃ (A posetive)
💉রক্তের পরিমান:  ১ ব্যাগ
⌚রক্তদানের সময়: আজকেই যত তারাতাড়ি সম্ভব
🏥রক্তদানের স্থানঃ আশা হসপিটাল , রাজশাহী 
☎যোগাযোগ:01741783528
"""

positive_sample_out_3 = {
    "blood_group": "A+",
    "bags_needed": "1",
    "patient": {
        "name":"",
        "gender": "",
        "age-group":"teenager"
    },
    "condition": "stone operation",
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

negative_sample_inp_1 = """
Blood donation is a great virtue. Donating blood in emergency can save many lives.
"""

negative_sample_out_1 = {
    "is_blood_donation_request": "false"
}

negative_sample_inp_2 = """
বিরামপুর ব্লাড ব্যাংকের নিয়মিত রক্তদাতা💉
Sajib SK ভাই একজন রক্তস্বল্পতা রোগীর জন্য তার মূল্যবান এক ব্যাগ B+🩸 লাল ভালোবাসা উপহার দিয়েছে। তাকে রক্ত দানের জন্য শুভেচ্ছা ও অভিনন্দন।
এটা তার ২১'তম রক্তদান
রোগী ও রক্তদাতার সুস্থতা ও দীর্ঘায়ু কামনা করছি
"""

negative_sample_out_2 = {
    "is_blood_donation_request": "false"
}