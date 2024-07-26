import requests
from bs4 import BeautifulSoup
import re

# Function to extract coordinates from a Wikipedia page
def extract_coordinates(soup):
    coords_div = soup.find('div', {'id': 'mw-indicator-coordinates'})
    if coords_div:
        coords_span = coords_div.find('span', {'class': 'geo-default'})
        if coords_span:
            coord_text = coords_span.get_text()
            match = re.search(r'([\-0-9\.]+)°N\s([\-0-9\.]+)°E', coord_text)
            if match:
                latitude = match.group(1)
                longitude = match.group(2)
                return latitude, longitude
    return None, None

# Function to scrape hospital names and links from the main page
def scrape_hospital_list(main_page_url):
    response = requests.get(main_page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    hospitals = []
    for li in soup.select('#mw-content-text ul li'):
        a = li.find('a')
        if a:
            name = a.get_text()
            link = None 
            if 'href' in a: 
                link = 'https://en.wikipedia.org' + a['href']
        else:
            name = li.get_text()
            link = None
        hospitals.append((name, link))
    return hospitals

# Function to visit each hospital page and extract coordinates
def scrape_hospital_coordinates(hospitals):
    results = []
    for name, link in hospitals:
        if link:
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            latitude, longitude = extract_coordinates(soup)
            results.append((name, link, latitude, longitude))
        else:
            results.append((name, None, None, None))
    return results

# Main function to run the scraping process
def main():
    main_page_url = 'https://en.wikipedia.org/wiki/List_of_hospitals_in_Bangladesh'
    hospitals = scrape_hospital_list(main_page_url)
    results = scrape_hospital_coordinates(hospitals[:2])

    for result in results:
        name, link, latitude, longitude = result
        print(f'Name: {name}')
        if link:
            print(f'Link: {link}')
        if latitude and longitude:
            print(f'Coordinates: Latitude {latitude}, Longitude {longitude}')
        print('---')

if __name__ == '__main__':
    main()
