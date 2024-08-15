import json
import csv

# Sample JSON data
data = {
    "blood_group": "O+",
    "bags_needed": "2",
    "mediator": {
        "username": ""
    },
    "patient": {
        "name": "",
        "age-group": ""
    },
    "condition": "Pregnancy issues",
    "location": "Health Aid Lalbagh road beside Ebne Sina hospital",
    "probable_day": "11/7/24",
    "probable_time": "Morning around 9 am",
    "contacts": [
        {
            "name": "",
            "contact_numbers": [
                "01710-827726"
            ],
            "relation_with_patient": "Patient's husband"
        }
    ],
    "compensation": {
        "transportation": "",
        "allowance": ""
    }
}

data = {
    "blood_group": "AB-",
    "bags_needed": "4",
    "mediator": {
        "username": ""
    },
    "patient": {
        "name": "",
        "age-group": ""
    },
    "condition": "Situation is critical",
    "location": "Birdem General Hospital",
    "probable_day": "",
    "probable_time": "",
    "contacts": [
        {
            "name": "",
            "contact_numbers": [
                "01851343649",
                "+8801705160855"
            ],
            "relation_with_patient": ""
        }
    ],
    "compensation": {
        "transportation": "",
        "allowance": ""
    }
}

# Flatten the JSON
rows = []
for contact in data['contacts']:
    # You can choose to handle multiple contact numbers differently if needed
    contact_numbers = '; '.join(contact['contact_numbers'])
    row = {
        'blood_group': data['blood_group'],
        'bags_needed': data['bags_needed'],
        'mediator_username': data['mediator']['username'],
        'patient_name': data['patient']['name'],
        'patient_age_group': data['patient']['age-group'],
        'condition': data['condition'],
        'location': data['location'],
        'probable_day': data['probable_day'],
        'probable_time': data['probable_time'],
        'contact_name': contact['name'],
        'contact_numbers': contact_numbers,
        'relation_with_patient': contact['relation_with_patient'],
        'compensation_transportation': data['compensation']['transportation'],
        'compensation_allowance': data['compensation']['allowance']
    }
    rows.append(row)

# Prepare CSV headers
headers = [
    'blood_group',
    'bags_needed',
    'mediator_username',
    'patient_name',
    'patient_age_group',
    'condition',
    'location',
    'probable_day',
    'probable_time',
    'contact_name',
    'contact_numbers',
    'relation_with_patient',
    'compensation_transportation',
    'compensation_allowance'
]

# Write to CSV file
with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print("CSV file has been created successfully.")
