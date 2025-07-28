import json

from dotenv import load_dotenv
load_dotenv()

def read_txt(path):
    """Reads a text file and returns its contents as a string."""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_txt(path, content):
    """Writes a string to a text file."""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_json(path):
    """Reads a JSON file and returns the parsed object (dict or list)."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, obj):
    """Serializes a Python object to a JSON file with indentation and Unicode support."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
