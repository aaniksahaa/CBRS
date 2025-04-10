import os
import glob
from concurrent.futures import ThreadPoolExecutor
from parser import parse_blood_donation_request
from util import write_json, read_json
from llmclients import *

# Define directories
INPUT_DIR = "loaded"
OUTPUT_ROOT_DIR = "parsed/single"

os.makedirs(OUTPUT_ROOT_DIR, exist_ok=True)

def get_output_dir(model_name: str, method: str):
    # dir1 = model_name.replace("/", "__").replace(":", "-")
    dir1 = MODEL_TO_CORE_MAP[model_name]
    dir2 = method
    return os.path.join(OUTPUT_ROOT_DIR, dir1, dir2)


# Model and method configuration
# model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
# method = "few_shot"

# Function to process a single JSON file
def process_json_file(json_filepath, index, model_name, method):
    try:
        # Extract the filename from the path
        filename = os.path.basename(json_filepath)
        output_dir = get_output_dir(model_name, method)

        os.makedirs(output_dir, exist_ok=True)

        output_filepath = os.path.join(output_dir, filename)

        # Check if the output file already exists
        if os.path.exists(output_filepath) and read_json(output_filepath)['model']:
            # print(f"SKIPPING: Output file {output_filepath} already exists")
            return {"index": index, "status": "skipped", "filename": filename}

        # Read the JSON file
        data = read_json(json_filepath)
        if not data:
            raise ValueError("Failed to read JSON data")

        # Extract the text and metadata
        text = data.get("text", "")
        metadata = data.get("metadata", {})
        if not text:
            raise ValueError("No 'text' field found in JSON")

        # Parse the blood donation request
        parsed_data = parse_blood_donation_request(
            text,
            model_name=model_name,
            method=method,
            metadata=metadata
        )

        # Save the parsed output to the output directory
        write_json(output_filepath, parsed_data)
        print(f"✅ Processed file {index+1}: {output_filepath}")
        return {"index": index, "status": "success", "filename": filename}

    except Exception as e:
        print(f"❌ Error processing file {index+1} ({json_filepath}): {str(e)}")
        return {"index": index, "status": "error", "filename": filename, "error": str(e)}

# Main function to handle multithreading
def process_json_files_multithreaded(json_files, model_name, method, num_workers=30):
    # Create a list of tasks with file path and index
    tasks = [(filepath, idx) for idx, filepath in enumerate(json_files)]
    
    # Use ThreadPoolExecutor to manage threads
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Submit all tasks and get futures
        futures = [
            executor.submit(process_json_file, filepath, index, model_name, method)
            for filepath, index in tasks
        ]
        
        # Collect results as they complete
        results = []
        for future in futures:
            results.append(future.result())
    
    # Print summary
    success_count = sum(1 for r in results if r["status"] == "success")
    skipped_count = sum(1 for r in results if r["status"] == "skipped")
    error_count = sum(1 for r in results if r["status"] == "error")
    print(f"\n✅✅✅\nProcessing complete: model = {model_name}, method = {method}")
    print(f"Total files: {len(json_files)}")
    print(f"Successful: {success_count}")
    print(f"Skipped (already processed): {skipped_count}")
    print(f"Errors: {error_count}")


MODEL_NAMES = [
    # "deepseek/deepseek-chat:free",
    "deepseek-ai/DeepSeek-V3",
    "gpt-4o-mini",
    "claude-3-haiku-20240307",
    # "gemini-2.0-flash",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "meta-llama/Llama-3.2-3B-Instruct-Turbo",
    # "meta-llama/llama-3.2-3b-instruct:free",
    # "meta-llama/llama-3.2-1b-instruct:free",
    # "meta-llama/llama-3.1-8b-instruct:free",
    # "google/gemma-3-27b-it:free",
    # "google/gemma-2-9b-it:free",
    "google/gemma-2-27b-it",
    # "google/gemma-2-9b-it",
    "Qwen/Qwen2.5-7B-Instruct-Turbo",
    "mistralai/Mistral-7B-Instruct-v0.3"
]

METHODS = [
    "few_shot",
    "zero_shot"
]

NUM_WORKERS = 5

def run_bulk_parsing(json_files):
    for model_name in MODEL_NAMES:
        for method in METHODS:
            process_json_files_multithreaded(json_files, 
                                             model_name, 
                                             method, 
                                             num_workers=NUM_WORKERS)

if __name__ == "__main__":
    # Get all JSON files from the "loaded" directory
    json_files = glob.glob(os.path.join(INPUT_DIR, "*.json"))
    
    if not json_files:
        print(f"No JSON files found in {INPUT_DIR}")
    else:
        print(f"Found {len(json_files)} JSON files in {INPUT_DIR}")
        # exit(0)
        run_bulk_parsing(json_files)