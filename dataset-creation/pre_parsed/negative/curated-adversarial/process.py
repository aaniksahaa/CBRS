from util import *
import glob
import json

# Get all JSON files from the 'raw' folder
json_files = glob.glob("raw/*.json")

# Initialize an empty list to store all combined data
combined = []

# Iterate through each JSON file
for file_path in json_files:
    data = read_json(file_path)
    combined.extend(data)

merged = []

for c in combined:
    for lang in ['en','bn','tbn']:
        d = {
            "text": c[lang],
            "is_blood_donation_request": False,
            "metadata": {
                "language": lang,
                "source": "curated-adversarial"
            }
        }
        merged.append(d)

manually_collected_negatives = read_json('./manually_collected_negatives.json')

merged.extend(manually_collected_negatives)

out_path = f'merged.json'

write_json(out_path, merged)

print(len(merged))

print(f"✅ JSON successfully parsed and written to {out_path}")