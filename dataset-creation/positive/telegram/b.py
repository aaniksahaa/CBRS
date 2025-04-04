import glob
import json

# Grab all JSON files inside the "parsed" folder
files = sorted(glob.glob("parsed/*.json"))

messages = []

c = 0

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if 'message' in data:
            c += 1
            ndata = {'is_blood_donation_request': True}
            ndata['text'] = data['message']
            del data['message']
            ndata.update(data)
            ndata['source'] = 'telegram'

            # Write messages to a new JSON array file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(ndata, f, ensure_ascii=False, indent=2)

print(c)
