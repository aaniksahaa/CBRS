import glob
import json

# Grab all JSON files inside the "parsed" folder
files = sorted(glob.glob("parsed/*.json"))

messages = []

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "message" in data:
            msg = {
                'text': data['message'],
                'source': 'telegram'
            }
            messages.append(msg)

# Write messages to a new JSON array file
with open("messages.json", "w", encoding="utf-8") as f:
    json.dump(messages, f, ensure_ascii=False, indent=2)

print(f"✅ Done. Extracted {len(messages)} messages into all_messages.json")
