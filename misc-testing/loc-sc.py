import requests
from bs4 import BeautifulSoup

# URL of the Wikipedia page
# url = "https://en.wikipedia.org/wiki/Anwer_Khan_Modern_Medical_College"
url = 'https://en.wikipedia.org/wiki/Ad-din_Women%27s_Medical_College'

# Fetch the content of the page
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the page content
soup = BeautifulSoup(response.text, 'html.parser')

# Define a list to hold location names
location_names = []

# Find all <div> elements with specific classes and extract text from <a> tags
for div_class in ['locality', 'country-name']:
    divs = soup.find_all('div', class_=div_class)
    for div in divs:
        links = div.find_all('a')
        for link in links:
            location_names.append(link.get_text())

# Join the location names with commas
location_string = ', '.join(location_names)
print(location_string)
