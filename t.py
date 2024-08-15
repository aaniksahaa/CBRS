from utils import * 
import csv 

messages = read_json('./dataset/demo-messages.json')

st = 1  # skip first empty one 
en = len(messages)

rows = []

for i in range(st,en):
    print(i)
    text = messages[i]
    data = read_json(f'./dataset/out/raw/{i}.json')

    has_contact = len(data['contacts']) > 0

    contact = data['contacts'][0] if has_contact else None  # just taking the first for now 

    if contact:
        contact_numbers = '; '.join(contact['contact_numbers'])

    row = {
        'text': text,
        'blood_group': data['blood_group'],
        'bags_needed': data['bags_needed'],
        'mediator_username': data['mediator']['username'],
        'patient_name': data['patient']['name'],
        'patient_age_group': data['patient']['age-group'],
        'condition': data['condition'],
        'location': data['location'],
        'probable_day': data['probable_day'],
        'probable_time': data['probable_time'],
        'contact_name': contact['name'] if has_contact else '',
        'contact_numbers': contact_numbers if has_contact else '',
        'relation_with_patient': contact['relation_with_patient'] if has_contact else '',
        'compensation_transportation': data['compensation']['transportation'],
        'compensation_allowance': data['compensation']['allowance']
    }
    rows.append(row)

# Prepare CSV headers
headers = [
    'text',
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
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)

print("CSV file has been created successfully.")

    



