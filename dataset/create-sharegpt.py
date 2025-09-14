import json

# Load your dataset (assuming it's in a file named 'dataset.json')
with open('./parsed_merged.json', 'r') as f:
    data = json.load(f)

print(len(data))

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


import json
import random

# Set a seed for reproducibility
random.seed(42)

# Load your dataset
with open('sharegpt_dataset.jsonl', 'r', encoding='utf-8') as f:
    lines = [json.loads(line) for line in f]

# Shuffle the dataset
total_samples = len(lines)
shuffled_data = lines.copy()
random.shuffle(shuffled_data)

# Calculate split sizes
train_size = int(0.8 * total_samples)
val_size = int(0.1 * total_samples)
test_size = total_samples - train_size - val_size  # Ensure exact 80-10-10

# Split the data
train_data = shuffled_data[:train_size]
val_data = shuffled_data[train_size:train_size + val_size]
test_data = shuffled_data[train_size + val_size:]

# Save the splits to separate JSONL files
with open('train.jsonl', 'w', encoding='utf-8') as f:
    for item in train_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

with open('validation.jsonl', 'w', encoding='utf-8') as f:
    for item in val_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

with open('test.jsonl', 'w', encoding='utf-8') as f:
    for item in test_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')