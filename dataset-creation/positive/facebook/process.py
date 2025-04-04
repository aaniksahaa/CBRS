import glob
import json
from pathlib import Path

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
                "text": entry.get("text", "").strip(),
                "source": "facebook",
                "source_url": entry.get("url", ""),
                "is_blood_donation_request": True
            }
            output.append(extracted)

print(len(output))

# Save to a file or print
with open("merged.json", "w", encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
