import json
import os
import tiktoken
from collections import defaultdict

# Initialize tiktoken encoder (using a common OpenAI model like gpt-3.5-turbo)
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Function to count tokens using tiktoken
def count_tokens(text):
    try:
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        print(f"Error counting tokens for text: {text}, Error: {e}")
        return 0

# Step 1: Read the JSON file with proper Unicode handling
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Step 2: Process data for source-based stats
def compute_source_stats(data):
    stats = {
        "positive": defaultdict(lambda: {"total_samples": 0, "total_tokens": 0}),
        "negative": defaultdict(lambda: {"total_samples": 0, "total_tokens": 0})
    }

    for entry in data:
        # Determine if positive or negative based on is_blood_donation_request
        category = "positive" if entry["is_blood_donation_request"] else "negative"
        # Access source from the metadata dictionary
        source = entry["metadata"]["source"]

        # Increment sample count
        stats[category][source]["total_samples"] += 1

        # Count tokens for the text
        token_count = count_tokens(entry["text"])
        stats[category][source]["total_tokens"] += token_count

    # Calculate average tokens for each source
    for category in stats:
        for source in stats[category]:
            total_samples = stats[category][source]["total_samples"]
            total_tokens = stats[category][source]["total_tokens"]
            stats[category][source]["avg_tokens"] = (
                round(total_tokens / total_samples, 2) if total_samples > 0 else 0
            )

    # Convert defaultdict to regular dict for JSON serialization
    return {
        "positive": dict(stats["positive"]),
        "negative": dict(stats["negative"])
    }

# Step 3: Process data for language-based stats
def compute_language_stats(data):
    stats = {
        "positive": defaultdict(lambda: {"total_samples": 0, "total_tokens": 0}),
        "negative": defaultdict(lambda: {"total_samples": 0, "total_tokens": 0})
    }

    for entry in data:
        # Determine if positive or negative based on is_blood_donation_request
        category = "positive" if entry["is_blood_donation_request"] else "negative"
        # Access language from the metadata dictionary
        language = entry["metadata"]["language"]

        # Increment sample count
        stats[category][language]["total_samples"] += 1

        # Count tokens for the text
        token_count = count_tokens(entry["text"])
        stats[category][language]["total_tokens"] += token_count

    # Calculate average tokens for each language
    for category in stats:
        for language in stats[category]:
            total_samples = stats[category][language]["total_samples"]
            total_tokens = stats[category][language]["total_tokens"]
            stats[category][language]["avg_tokens"] = (
                round(total_tokens / total_samples, 2) if total_samples > 0 else 0
            )

    # Convert defaultdict to regular dict for JSON serialization
    return {
        "positive": dict(stats["positive"]),
        "negative": dict(stats["negative"])
    }

# Step 4: Save stats to JSON files
def save_stats(stats, filename, output_dir="dataset_stats"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
    print(f"Saved stats to {filepath}")

# Main function to process the dataset
def main():
    # Path to the JSON file
    json_file = "pre_parsed_merged.json"
    
    # Read the JSON data
    data = read_json_file(json_file)
    
    # Compute source-based stats
    source_stats = compute_source_stats(data)
    save_stats(source_stats, "source_stats.json")
    
    # Compute language-based stats
    language_stats = compute_language_stats(data)
    save_stats(language_stats, "language_stats.json")

if __name__ == "__main__":
    main()