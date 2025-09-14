import glob
import os
from util import *

def get_all_jsons(directory_path):
    """
    Returns a list of filepaths for all JSON files in the specified directory.
    
    Args:
        directory_path (str): Path to the directory to search for JSON files
        
    Returns:
        list: List of full filepaths to JSON files
    """
    # Ensure the directory path ends with a separator
    directory_path = os.path.normpath(directory_path) + os.sep
    
    # Use glob to find all .json files in the directory
    json_files = glob.glob(directory_path + "*.json")
    
    return json_files

jsons = get_all_jsons('./parsed/single/gold')

data = []

for json in jsons:
    j = read_json(json)
    d = {
        "text": j["blood_donation_request_text"],
        "is_blood_donation_request": j["is_blood_donation_request"],
        "parsed_json": j["parsed_json"],
        "metadata": j["blood_donation_request_metadata"]
    }
    data.append(d)

write_json('./parsed/parsed_merged.json', data)