import math 
import re
import json
from bs4 import BeautifulSoup
import requests

def read_json(json_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def write_json(filename, data):
    j = json.dumps(data, indent=4)
    with open(filename, 'w') as json_file:
        json_file.write(j)

def write_txt(filename, text, mode='w'):
    with open(filename, mode, encoding='utf-8') as f:
        f.write(text)

def read_txt(filename):
    with open(filename) as f:
        content = f.read()
    return content