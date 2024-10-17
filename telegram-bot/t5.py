import json 

def parse_int(s):
    try:
        return int(s)
    except Exception:
        return None 

d = {
    "is_seeking_blood_donation": "true",
    "blood_group": "B-",
    "bags_needed": "",
    "patient": {
        "name": "",
        "gender": "",
        "age_group": ""
    },
    "condition": "Critical situation",
    "location": "BRB Hospital,Panthapath",
    "hospital_name": "BRB Hospital",
    "location_markers": [
        "Panthapath"
    ],
    "probable_day": "today",
    "probable_time": "in the afternoon",
    "contacts": [
        {
            "name": "",
            "contact_numbers": [
                "01877621398"
            ],
            "relation_with_patient": ""
        }
    ],
    "compensation": {
        "transportation": "",
        "allowance": ""
    }
}

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

print(data)

data = {
        "messageText": "Urgent blood needed",
        "bloodGroup": "A+",
        "bagsNeeded": 2,
        "patientName": "John Doe",
        "patientGender": "male",
        "patientAgeGroup": "adult",
        "condition": "surgery",
        "location": "Dhaka",
        "hospitalName": "Square Hospital",
        "locationMarkers": ["Dhaka", "Banani"],
        "probableDay": "2024-03-20",
        "probableTime": "10:00 AM",
        "transportation": "Y",
        "allowance": "Y",
        "sourceTelegramChatId": "123456789",
        "contacts": [
            {
                "name": "Jane Doe",
                "numbers": ["+8801712345678", "+8801812345678"],
                "relationWithPatient": "sister"
            },
            {
                "name": "John Smith",
                "numbers": ["+8801612345678"],
                "relationWithPatient": "friend"
            }
        ]
    }