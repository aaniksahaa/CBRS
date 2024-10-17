import os
import json

def merge_json_files(input_dir, output_file):
    merged_data = []  # Initialize an empty list to hold merged data

    # Loop through all files in the specified directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):  # Check for JSON files
            file_path = os.path.join(input_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)  # Load the JSON data
                if isinstance(data, list):  # Ensure it's a list
                    merged_data.extend(data)  # Merge the arrays

    # Write the merged data to the output JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)

# Usage
input_directory = './neg-jsons'  # Specify your directory path
output_json_file = 'merged_negative_samples.json'  # Specify the output file name
merge_json_files(input_directory, output_json_file)
