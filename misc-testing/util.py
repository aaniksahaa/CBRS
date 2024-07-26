import math 
import re
import json
from bs4 import BeautifulSoup
import requests

def read_json(json_file_path):
    with open('data/' + json_file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def write_json(filename, data):
    j = json.dumps(data, indent=4)
    with open('data/'+filename, 'w') as json_file:
        json_file.write(j)

def write_txt(filename, text, mode='w'):
    with open(filename, mode, encoding='utf-8') as f:
        f.write(text)

def read_txt(filename):
    with open(filename) as f:
        content = f.read()
    return content


def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance

# Example usage
# lat1, lon1 = 23.745654, 90.382433  # Coordinate 1
# lat2, lon2 = 23.8103, 90.4125     # Coordinate 2 (e.g., Dhaka, Bangladesh)

# distance = haversine(lat1, lon1, lat2, lon2)
# print(f"Distance: {distance:.2f} km")

