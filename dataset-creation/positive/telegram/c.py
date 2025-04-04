import glob
import json
import os 

# Grab all JSON files inside the "parsed" folder
files = sorted(glob.glob("parsed/*.json"))

messages = []

c = 0

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if 'blood_donation_related' in data and data['blood_donation_related'] == "false":
            c += 1
            print(file_path)
            # os.remove(file_path)

print(c)
