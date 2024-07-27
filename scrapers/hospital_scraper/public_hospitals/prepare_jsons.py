import os
import pandas as pd
import json
import tabula
import csv 
from util import * 
import re

def remove_code_pattern(input_string):
    # Define the regex pattern
    pattern = r'\(Code:\d+\)'
    
    # Substitute the pattern with an empty string
    result = re.sub(pattern, '', input_string)
    
    return result

def convert_keys_to_lowercase(data):
    if isinstance(data, list):
        return [convert_keys_to_lowercase(item) for item in data]
    elif isinstance(data, dict):
        return {k.lower(): convert_keys_to_lowercase(v) for k, v in data.items()}
    else:
        return data
    
def process(data):
    ndata = []
    for d in data:
        nd = {}
        if(d.get('Email','') == 'Email'):
            continue
        for k,v in d.items():
            k = k.lower()
            if 'bed' in k:
                k = 'num_beds'
            elif 'no' in k or 'sl' in k:
                continue
            elif k == 'organization name' or k == 'name of facility':
                k = 'name'
                v = remove_code_pattern(v).strip()
            elif 'phone' in k or 'mobile' in k:
                k = 'contact'
                items = v.split('/')
                v = []
                for item in items:
                    item = item.strip()
                    if(len(item)>0):
                        v.append(item)
            elif 'division' in k:
                k = 'division'
            elif 'district' in k:
                k = 'district'
            elif 'upazila' in k:
                k = 'upazila'
            nd[k] = v 
        ndata.append(nd)
    return ndata
            

def convert_pdf_to_csv(pdf_path, csv_path):
    # Extract tables from the PDF and save as CSV
    tabula.convert_into(pdf_path, csv_path, output_format="csv", pages='all')

def convert_csv_to_json(csv_path, json_path):
    # Read CSV and convert to JSON
    data = []
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)

    data = process(data)

    write_json(json_path, data)

def process_folder(input_folder, output_folder):
    # Traverse through all PDFs in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            base_name = os.path.splitext(filename)[0]
            csv_path = os.path.join(output_folder, f"{base_name}.csv")
            json_path = os.path.join(output_folder, f"{base_name}.json")

            print(f"Processing {pdf_path}...")
            convert_pdf_to_csv(pdf_path, csv_path)
            convert_csv_to_json(csv_path, json_path)
            print(f"Converted {pdf_path} to {json_path}")

input_folder = 'raw'
output_folder = 'preprocessed'

# Make sure the output folder exists
os.makedirs(output_folder, exist_ok=True)

process_folder(input_folder, output_folder)
