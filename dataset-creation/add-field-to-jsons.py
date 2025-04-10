import os
import json

# Define the base directory where the JSON files are located
base_dir = "parsed/single"

# Function to process JSON files in a given directory and add the method property
def process_json_files(directory, method_value):
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                try:
                    # Read the JSON file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Add the new "method" property
                    data["method"] = method_value

                    # Write the modified JSON back to the file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print(f"Updated {file_path} with method: {method_value}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

# Get all model directories under parsed/single
model_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

# Process each model directory
for model in model_dirs:
    # Process the "few_shot" directory for the current model
    few_shot_dir = os.path.join(base_dir, model, "few_shot")
    if os.path.exists(few_shot_dir):
        print(f"Processing few_shot for model: {model}")
        process_json_files(few_shot_dir, "few_shot")
    else:
        print(f"No few_shot directory found for model: {model}")

    # Process the "zero_shot" directory for the current model
    zero_shot_dir = os.path.join(base_dir, model, "zero_shot")
    if os.path.exists(zero_shot_dir):
        print(f"Processing zero_shot for model: {model}")
        process_json_files(zero_shot_dir, "zero_shot")
    else:
        print(f"No zero_shot directory found for model: {model}")