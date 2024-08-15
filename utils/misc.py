import re 
import os 
from .constants import * 
import pickle
import json 

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


def debug(x):
    if ENV == 'development':
        print(x)

# CONSOLE INPUTS

def input_choice(title, options):
    debug(f'\nPlease choose carefully.\n{title}\n')
    for index, option in enumerate(options):
        debug(f'{index+1}. {option}')
    while True:
        try:
            choice = int(input("\nPlease choose: "))
            if 1 <= choice <= len(options):
                return choice
            else:
                debug(f"Invalid choice. Please enter a number between 1 and {len(options)}.")
        except ValueError:
            debug("Invalid input. Please enter a number.")

def input_yes_no(title):
    debug(f'\n{title}\n')
    while True:
        choice = input("\nPlease choose Y or N: ").lower()
        if choice == 'y':
            return True 
        elif choice == 'n':
            return False
        else:
            debug(f"Invalid choice. Please enter Y or N.")

# DIRECTORY

def create_directory(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"Directory '{directory_path}' created successfully")
    except OSError as error:
        print(f"Error creating directory '{directory_path}': {error}")

def get_filename_core(filename):
    filename_core = os.path.splitext(filename)[0]
    return filename_core

# READ WRITE

def write_pickle(dir, filename, obj):
    filepath = os.path.join(dir, filename)
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)

def read_pickle(dir, filename):
    filepath = os.path.join(dir, filename)
    with open(filepath, 'rb') as f:
        obj = pickle.load(f)
    return obj

def read_txt(dir, filename):
    filepath = os.path.join(dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def write_txt(dir, filename, text):
    filepath = os.path.join(dir, filename)
    with open(filepath,'w') as f:
        f.write(text)

def write_file(dir, filename, content):
    filepath = os.path.join(dir, filename)
    with open(filepath,'w') as f:
        f.write(content)

def read_json(dir, filename):
    filepath = os.path.join(dir, filename)
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data

def write_json(dir, filename, obj):
    filepath = os.path.join(dir, filename)
    with open(filepath,'w') as f:
        f.write(json.dumps(obj,indent=2))

# STRING OPERATIONS

def get_lines(text):
    return text.split('\n')

# REGEX OPERATIONS

def multiple_replace(text, replacements, mode='normal'):
    patterns = [rf'{re.escape(key)}' for key in replacements.keys()]
    if mode == 'abbr':
        patterns = [rf'(?<!\()\b{re.escape(key)}\b(?!\))' for key in replacements.keys()]
    
    pattern = '|'.join(patterns)

    # debug(pattern)

    # Create a regular expression from all the keys in the replacements dictionary
    # regex = re.compile("|".join(map(re.escape, replacements.keys())))

    regex = re.compile(pattern)

    # Define a function to replace each match with the corresponding value from the dictionary
    def replace(match):
        return replacements[match.group(0)]

    # Use re.sub to replace all occurrences
    return regex.sub(replace, text)

# PARSING

def parse_message_to_json(format_string):
    # Regular expression pattern to extract key-value pairs
    # as <KEY = VALUE>
    pattern = r'<(\w+)\s*=\s*([^>]+)>'
    matches = re.findall(pattern, format_string)

    # Create a dictionary from the matches
    result = {key: value.strip() for key, value in matches}

    return result

def extract_reference_ids(text):
    pattern = r'(?:REFERENCE_IDS|REFERENCES_ID|REFERENCES_IDS|REFERENCE_ID)[\s:=<\*]*([\d,\s]+)[>\s]*'
    matches = re.findall(pattern, text)
    
    reference_ids = []
    modified_text = text
    for match in matches:
        ids = [int(num.strip()) for num in match.split(',')]
        reference_ids.extend(ids)
    if 'REFERENCE_ID' in modified_text:
        modified_text = modified_text.split('REFERENCE_ID')[0]
    if 'Final Answer:' in modified_text:
        final_answer = modified_text.split('Final Answer:')[1].strip()
    else:
        final_answer = modified_text.replace('Thought:','').replace('Final Answer:','')
    return reference_ids, final_answer

def parse_llm_output(text):
    """
    Extracts reference IDs from the given text, returns them as a list of integers, and
    removes the reference IDs section from the original text.

    :param text: A string containing reference IDs in the format <REFERENCE_ID = ...>
    :return: A tuple containing a list of integers representing the reference IDs and the final answer
    """
    pattern = r'(?:<REFERENCE_ID\s*[:=]\s*|REFERENCE_ID\s*[:=]\s*<)\s*([\d,\s]+)\s*>'
    match = re.search(pattern, text)
    
    if match:
        reference_ids = [int(num.strip()) for num in match.group(1).split(',')]
        modified_text = re.sub(pattern, '', text)  # Remove the reference IDs section
        modified_text = modified_text.replace('<>','')
        final_answer = modified_text
        if 'Final Answer:' in modified_text:
            final_answer = modified_text.split('Final Answer:')[1].strip()
        else:
            final_answer = modified_text.replace('Thought:','').replace('Final Answer:','')
        return reference_ids, final_answer
    else:
        reference_ids, final_answer = extract_reference_ids(text)
        return reference_ids, final_answer

def is_int(value):
    try:
        v = int(value)
        return True
    except (ValueError, TypeError):
        return False

def get_int(value):
    """
    Converts a string to an integer. If the conversion fails, returns -1.

    :param value: The string to convert to an integer.
    :return: The converted integer or -1 if the conversion fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return -1
    
def show_banner(t):
    return f"\n\n{'*'*20}\n\n{t}\n\n{'*'*20}\n\n"
