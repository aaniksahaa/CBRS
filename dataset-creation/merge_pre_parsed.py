import os
import json

from util import *

def collect_merged_json_files(directory):
    """
    Recursively collect all merged.json files and combine their contents into a single array
    """
    combined_array = []
    
    # Walk through the directory tree
    for root, dirs, files in os.walk(directory):
        # Check if merged.json exists in current directory
        if "merged.json" in files:
            file_path = os.path.join(root, "merged.json")
            try:
                # Read and load the JSON file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure the loaded data is a list/array
                    if isinstance(data, list):
                        combined_array.extend(data)
                    else:
                        print(f"Warning: {file_path} does not contain a JSON array, skipping")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {file_path}: {e}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    return combined_array

def main():
    # Target directory relative to script location
    target_dir = "./pre_parsed"
    
    # Check if directory exists
    if not os.path.exists(target_dir):
        print(f"Error: Directory {target_dir} does not exist")
        return
    
    # Collect all merged.json contents
    combined_data = collect_merged_json_files(target_dir)

    manually_collected_negatives = read_json('./pre_parsed/positive/facebook/manually_collected_negatives.json')
    combined_data.extend(manually_collected_negatives)

    # Save the combined array to a new file
    output_file = "pre_parsed_merged.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully combined {len(combined_data)} items into {output_file}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()