import json

# Load your dataset (assuming it's in a file named 'dataset.json')
with open('dataset.json', 'r') as f:
    data = json.load(f)

# Convert to ShareGPT format
sharegpt_data = []
for entry in data:
    conversation = [
        {"from": "human", "value": entry["text"]},
        {"from": "gpt", "value": json.dumps(entry["parsed_json"])}
    ]
    sharegpt_data.append({"conversations": conversation})

# Save to JSONL file
with open('sharegpt_dataset.jsonl', 'w') as f:
    for item in sharegpt_data:
        f.write(json.dumps(item) + '\n')