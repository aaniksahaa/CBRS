import sys 
sys.path.append(".")

import re
import json
from bs4 import BeautifulSoup
import requests
import os 
from datetime import datetime 
from tqdm import tqdm

# must run from root, otherwise, paths will be altered

def read_json(json_file_path):
    with open('data/' + json_file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def write_json(filename, data):
    j = json.dumps(data, indent=4)
    with open('data/'+filename, 'w') as json_file:
        json_file.write(j)

def write_txt(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def fetch_data_with_requests(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return '#' 
    except requests.RequestException:
        return '#'
    
url = 'http://103.247.238.81/hsmdghs/registration/hsm_facility_show_public.php'

print(fetch_data_with_requests(url))