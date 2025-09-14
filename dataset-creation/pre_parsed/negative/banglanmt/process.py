import os
import json
from util import * 

# Define the path to the 'raw' folder
raw_folder_path = "raw"

# Initialize a list to store all JSON entries
json_data = []

# Function to process a file and add its sentences to the JSON data
def process_file(file_path, language):
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read all lines and strip any whitespace
        lines = [line.strip() for line in f.readlines() if line.strip()]  # Ignore empty lines
        
        # For each line, create a JSON entry
        for line in lines:
            entry = {
                "text": line,
                "is_blood_donation_request": False,
                "metadata": {
                    "language": language,
                    "source": "banglanmt"
                }
            }
            json_data.append(entry)

# Iterate through all files in the 'raw' folder
for filename in os.listdir(raw_folder_path):
    file_path = os.path.join(raw_folder_path, filename)
    
    # Check if it's a file (not a directory)
    if os.path.isfile(file_path):
        # Determine the language based on the filename
        # Assuming files are named in a way that indicates language (e.g., "RisingNews.test.bn" for Bangla)
        if "bn" in filename.lower():
            language = "bn"
        elif "en" in filename.lower():
            language = "en"
        else:
            # Skip files that don't match expected language patterns
            continue
        
        # Process the file
        process_file(file_path, language)

# Write the collected data to a JSON file
output_file = "output.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

print(f"JSON file '{output_file}' has been generated with {len(json_data)} entries.")

out_path = f'merged.json'

write_json(out_path, json_data)

print(f"✅ JSON successfully parsed and written to {out_path}")