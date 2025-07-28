from util import *
from detect_language import *

s = read_txt('raw/messages.txt')

sep = 20*"*"

messages = s.split(sep)

merged = []

for m in messages:
    text = m.strip()
    d = {
        "text": text,
        "is_blood_donation_request": True,
        "metadata": {
            "language": detect_language(text),
            "source": "telegram"
        }
    }
    merged.append(d)

out_path = 'merged.json'

# Step 3: Save it as a clean .json file
write_json(out_path, merged)

print(f"{len(merged)} positive samples found.")

print(f"✅ JSON successfully parsed and written to {out_path}")