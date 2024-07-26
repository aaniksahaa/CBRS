import requests
import re

# URL of the Wikipedia page
url = "https://en.wikipedia.org/wiki/Anwer_Khan_Modern_Medical_College"

# Fetch the content of the page
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Find all href attributes in the page content
href_pattern = re.compile(r'href="(https://geohack.toolforge.org/geohack\.php\?pagename=[^"]+&amp;params=[^"]+)"')
href_matches = href_pattern.findall(response.text)

# Pattern to extract coordinates and single-letter directions from the href
coord_pattern = re.compile(r'params=([\-0-9\.]+)_([NSEW])_([\-0-9\.]+)_([NSEW])')

for href in href_matches:
    match = coord_pattern.search(href)
    if match:
        latitude = match.group(1)
        lat_direction = match.group(2)
        longitude = match.group(3)
        long_direction = match.group(4)
        print(f'Latitude: {latitude} {lat_direction}, Longitude: {longitude} {long_direction}')
    else:
        print("Coordinates not found in href:", href)
