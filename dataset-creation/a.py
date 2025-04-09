from util import *

a = read_json('./pre_parsed_merged.json')

import json
import hashlib
import os
from pathlib import Path

# Directory where individual JSON files will be saved
OUTPUT_DIR = "loaded"

# Ensure the output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def calculate_hash(json_obj):
    """
    Calculate a SHA-256 hash of the JSON object based on its content.
    We convert the JSON object to a string with sorted keys to ensure consistency.
    """
    # Convert the JSON object to a string with sorted keys for consistent hashing
    json_str = json.dumps(json_obj, sort_keys=True)
    # Create a SHA-256 hash
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    return hash_obj.hexdigest()

def save_json_to_file(json_obj, output_dir):
    """
    Save a JSON object to a file named with its content hash.
    Returns True if the file was created, False if it already existed.
    """
    # Calculate the hash of the JSON object
    file_hash = calculate_hash(json_obj)
    # Define the output file path
    output_file = os.path.join(output_dir, f"{file_hash}.json")
    
    # Check if the file already exists
    if os.path.exists(output_file):
        print(f"File {output_file} already exists, skipping...")
        return False
    
    # Save the JSON object to the file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, indent=4)
    print(f"Saved {output_file}")
    return True

def process_json_dataset(json_data, output_dir):
    """
    Process a list of JSON objects and save each to an individual file.
    """
    new_files_count = 0
    for json_obj in json_data:
        if save_json_to_file(json_obj, output_dir):
            new_files_count += 1
    print(f"Processed {len(json_data)} JSON objects, created {new_files_count} new files.")

# Example usage
if __name__ == "__main__":
    # Sample JSON data (replace this with your actual JSON data)
    json_data = [
        {
            "text": "Blood Donor Needed!!!\nBlood group: AB +ve\nQUANTITY: 1 bag\nContact: +880916436",
            "is_blood_donation_request": True,
            "metadata": {
                "language": "tbn",
                "source": "facebook"
            }
        },
        {
            "text": "রক্তদাতা AB+ রুগী প্রয়োজন, নিকটতম রক্তদাতা এই রুগীর জন্য, কেট হয়ে সাহায্য করুন বাংলাদেশি",
            "is_blood_donation_request": True,
            "metadata": {
                "language": "bn",
                "source": "facebook"
            }
        }
        # Add more JSON objects as needed
    ]

    # Process the JSON dataset
    process_json_dataset(json_data, OUTPUT_DIR)

    # Simulate adding new JSON objects later
    new_json_data = [
        # Existing object (should be skipped)
        {
            "text": "Blood Donor Needed!!!\nBlood group: AB +ve\nQUANTITY: 1 bag\nContact: +880916436",
            "is_blood_donation_request": True,
            "metadata": {
                "language": "tbn",
                "source": "facebook"
            }
        },
        # New object (should be saved)
        {
            "text": "Urgent Blood Donor Needed for O+ in Dhaka",
            "is_blood_donation_request": True,
            "metadata": {
                "language": "en",
                "source": "twitter"
            }
        }
    ]

    print("\nProcessing new JSON data...")
    process_json_dataset(new_json_data, OUTPUT_DIR)