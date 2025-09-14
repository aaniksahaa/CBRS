import pandas as pd
import json

# Define the path to the CSV file
csv_file_path = "raw/BanglaTLIT_train.csv"

# Define the maximum number of entries to include in the output
max_entries = 5000  # You can change this to your desired number

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Filter rows where both 'text_transliterated' and 'text_bengali' are non-empty
df_paired = df[
    df['text_transliterated'].notna() & 
    df['text_transliterated'].str.strip().astype(bool) & 
    df['text_bengali'].notna() & 
    df['text_bengali'].str.strip().astype(bool)
]

# Initialize a list to store all text entries with their lengths and languages
text_entries = []

# Process the paired rows
for _, row in df_paired.iterrows():
    # Add the transliterated text (tbn)
    text_entries.append({
        "text": row['text_transliterated'].strip(),
        "length": len(row['text_transliterated'].strip()),
        "language": "tbn"
    })
    
    # Add the Bangla text (bn)
    text_entries.append({
        "text": row['text_bengali'].strip(),
        "length": len(row['text_bengali'].strip()),
        "language": "bn"
    })

# Sort the entries by length in descending order
text_entries.sort(key=lambda x: x["length"], reverse=True)

# Limit to the max number of entries
if len(text_entries) > max_entries:
    text_entries = text_entries[:max_entries]

# Create JSON entries
json_data = []
for entry in text_entries:
    json_entry = {
        "text": entry["text"],
        "is_blood_donation_request": False,
        "metadata": {
            "language": entry["language"],
            "source": "banglatlit"
        }
    }
    json_data.append(json_entry)

print(len(json_data))

# Write the collected data to a JSON file
out_path = 'merged.json'

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print(f"✅ JSON successfully parsed and written to {out_path}")