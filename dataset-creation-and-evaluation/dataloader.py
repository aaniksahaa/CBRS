import json
import os
import uuid
import random
from collections import defaultdict

import hashlib

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

# Function to sample messages based on the given ratio
def sample_data(dataset_file, output_folder, N, ratio_en, ratio_bn, ratio_tbn):
    # Step 1: Load the JSON dataset
    with open(dataset_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if N == -1:
        N = len(data)

    # Step 2: Filter true blood donation requests and group by language
    language_groups = defaultdict(list)
    for entry in data:
        if entry.get("is_blood_donation_request", False):  # Filter true requests
            language = entry.get("metadata", {}).get("language", "unknown")
            if language in ["en", "bn", "tbn"]:  # Only consider en, bn, tbn
                language_groups[language].append(entry)

    # Step 3: Calculate the number of messages to sample from each language
    total_ratio = ratio_en + ratio_bn + ratio_tbn
    if total_ratio == 0:
        raise ValueError("The sum of the ratios must be greater than 0")

    num_en = int(N * (ratio_en / total_ratio))
    num_bn = int(N * (ratio_bn / total_ratio))
    num_tbn = N - num_en - num_bn  # Ensure the total adds up to N

    print(f"Sampling: {num_en} en, {num_bn} bn, {num_tbn} tbn messages")

    # Step 4: Sample messages from each language group
    sampled_messages = []
    for lang, count in [("en", num_en), ("bn", num_bn), ("tbn", num_tbn)]:
        messages = language_groups[lang]
        if len(messages) < count:
            print(f"Warning: Not enough {lang} messages. Requested {count}, but only {len(messages)} available.")
            count = len(messages)
        sampled = random.sample(messages, count)  # Randomly sample the required number
        sampled_messages.extend(sampled)

    # Step 5: Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Step 6: Save each sampled message as a separate JSON file with a UUID filename
    for message in sampled_messages:
        # Calculate the hash of the JSON object
        file_hash = calculate_hash(message)
        output_filepath = os.path.join(output_folder, f"{file_hash}.json")

        # Check if the file already exists
        if os.path.exists(output_filepath):
            print(f"\n\nFile {output_filepath} already exists, skipping...\n\n")
            continue
        
        # Save the message to a file
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(message, f, ensure_ascii=False, indent=4)

        print(f"Saved message to {output_filepath}")

# Example usage
dataset_file = "./pre_parsed_merged.json"  # Path to your JSON dataset
output_folder = "loaded"  # Folder to save the sampled messages
N = -1  # Total number of messages to sample
ratio_en = 4  # Ratio for English messages
ratio_bn = 4  # Ratio for Bangla messages
ratio_tbn = 3  # Ratio for transliterated Bangla messages

sample_data(dataset_file, output_folder, N, ratio_en, ratio_bn, ratio_tbn)