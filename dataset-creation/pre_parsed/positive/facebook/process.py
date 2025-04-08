import glob
import json
from pathlib import Path
from detect_language import *
from util import *

output = []

# Adjust the path pattern based on your actual folder structure
json_files = glob.glob("raw/*.json")

manually_collected_negatives = read_json('./manually_collected_negatives.json')

negative_texts = set()
for d in manually_collected_negatives:
    negative_texts.add(d['text'])

# print(negative_texts)

for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        for entry in data:
            ok = True
            text = entry.get("text", "").strip()
            # as a simple heuristic, we threshold based on length
            # to omit the few number of negatives
            if len(text) < 50 or len(text) > 800:
                continue

            if text in negative_texts:
                continue

            # handling a common case in groups
            # omitting posts like 'Let's welcome our new members'
            if 'welcome' in text.lower() and 'new member' in text.lower():
                continue
            
            # as a heuristic, texts containing links are considered non request
            # don't cringe please :')
            negative_keywords = ['http', 'মাদ্রাসা', 'ভালোবাসা', 'ভালবাসা', 'ত্রাণ', 'ত্রান']
            if any(keyword in text for keyword in negative_keywords):
                continue

            extracted = {
                "text": text,
                "is_blood_donation_request": True,
                "metadata": {
                    "language": detect_language(text),
                    "source": "facebook"
                }
            }
            output.append(extracted)

print(len(output))

out_path = 'merged.json'

# Save to a file or print
with open(out_path, "w", encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ JSON successfully parsed and written to {out_path}")
