from util import *

def get_requests_from_txt(path):
    j = read_txt(path)
    data = json.loads(j)
    return data

paths = ['raw/BDC.txt', 'raw/HO.txt', 'raw/PDR.txt']

requests = []

for path in paths:
    requests.extend(get_requests_from_txt(path))

merged_pos = []

for r in requests:
    if 'blood required' in r and r['blood required'] == "1":
        data = {
            'text': r['text'],
            'language': 'en',
            'source': 'ebdr-twitter',
            'is_blood_donation_request': True
        }
        merged_pos.append(data)

out_path = 'merged.json'

# Step 3: Save it as a clean .json file
write_json(out_path, merged_pos)

print(f"{len(merged_pos)} positive samples found.")

print(f"✅ JSON successfully parsed and written to {out_path}")