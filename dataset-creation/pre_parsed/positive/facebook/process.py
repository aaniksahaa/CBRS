import glob
import json
from pathlib import Path
from detect_language import *

output = []

# Adjust the path pattern based on your actual folder structure
json_files = glob.glob("raw/*.json")

for file_path in json_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

        for entry in data:
            text = entry.get("text", "").strip()
            # as a simple heuristic, we threshold based on length
            # to omit the few number of negatives
            if len(text) < 30:
                continue
            # handling a common case in groups
            # omitting posts like 'Let's welcome our new members'
            if 'welcome' in text.lower() and 'new member' in text.lower():
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
