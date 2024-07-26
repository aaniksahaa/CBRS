import requests
from bs4 import BeautifulSoup
import re
from coord import Coord
import json 
import time 

# Base URL for Wikipedia
BASE_URL = 'https://en.wikipedia.org'

def fetch_hospital_list(url):
    # Fetch the content of the Wikipedia page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all hospital names and links
    hospital_list = []

    for li in soup.select('#mw-content-text ul li')[:]:
        core_name = None 
        name = li.get_text()
        if 'Timor' in name:
            break
        if len(name) < 15:
            continue
        link = None 
        a_tag = li.find('a')
        if a_tag:
            # print(f'a tag found\n{a_tag}')

            core_name = a_tag.get_text()
            href = a_tag.get('href',None)

            if href is not None:
                link = BASE_URL + href
        else:
            name = li.get_text()

        print(f'\nName: {name}\nLink: {link}\n')
        hospital_list.append((core_name, name, link))

    return hospital_list

def fetch_hospital_location(url):
    attempts = 3
    for attempt in range(attempts):
        try:
            # Fetch the content of the Wikipedia page
            response = requests.get(url)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            time.sleep(0.5)  # Optional: wait for a second before retrying
            if attempt == attempts - 1:
                print(f"Sorry! Error fetching the page for {url}")
                return None, None
    
    # Fetch the content of the page
    # response = requests.get(url)

    ######################
    # Extract co-ordinates
    ######################

    # Find all href attributes in the page content
    href_pattern = re.compile(r'href="(https://geohack.toolforge.org/geohack\.php\?pagename=[^"]+&amp;params=[^"]+)"')
    href_matches = href_pattern.findall(response.text)

    # Pattern to extract coordinates and single-letter directions from the href
    coord_pattern = re.compile(r'params=([\-0-9\.]+)_([NSEW])_([\-0-9\.]+)_([NSEW])')

    coord = None 

    if href_matches:
        href = href_matches[0]
        match = coord_pattern.search(href)
        if match:
            latitude = match.group(1)
            lat_direction = match.group(2)
            longitude = match.group(3)
            long_direction = match.group(4)

            coord = Coord(latitude,lat_direction,longitude,long_direction)

            print(coord)
        else:
            print("Coordinates not found in href:", href)

    #########################
    # Extract location detail
    #########################

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
            
    return coord, location_names

# def fetch_hospital_details(url):
#     response = requests.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Extract location information
#     location = None
#     infobox = soup.find('table', {'class': 'infobox'})
#     if infobox:
#         location_td = infobox.find('td', text=re.compile('Location'))
#         if location_td:
#             location = location_td.find_next_sibling('td')
#             if location:
#                 location = location.get_text(strip=True)

#     # Extract coordinates
#     coordinates = None
#     coordinates_div = soup.find('div', {'id': 'coordinates'})
#     if coordinates_div:
#         coordinate_link = coordinates_div.find('a', href=True)
#         if coordinate_link:
#             coordinates = coordinate_link.get_text(strip=True)

#     return location, coordinates

def main():
    url = 'https://en.wikipedia.org/wiki/List_of_hospitals_in_Bangladesh'
    hospitals = fetch_hospital_list(url)[:]

    print(len(hospitals))

    # exit()

    hospitals_arr = []

    i = 1

    for core_name, name, link in hospitals:
        print(f"Hospital Name: {name}")
        coord_dict = {}
        if link:
            coord, location_names = fetch_hospital_location(link)
            if coord:
                print(f"  Co-ordinates: {coord}")
                coord_dict = coord.to_dict()
            if location_names:
                print(f"  Location: {','.join(location_names)}")
        h = {
            'core_name': core_name,
            'name': name,
            'coord': coord_dict,
            'location_names': location_names
        }
        hospitals_arr.append(h)
        print()

        i += 1
        if(i % 10 == 0):
            with open('hospitals.json','w') as f:
                f.write(json.dumps(hospitals_arr,indent=2))


    with open('hospitals.json','w') as f:
        f.write(json.dumps(hospitals_arr,indent=2))

if __name__ == '__main__':
    main()
