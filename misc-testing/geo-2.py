import requests
import json
import time

# Set the base URL for the Nominatim API
BASE_URL = "https://nominatim.openstreetmap.org"

# Custom User-Agent or Referer
HEADERS = {
    'User-Agent': 'Bloodbot/1.0 openmaster.2001@gmail.com',
    'Referer': 'https://bloodbot43.com'
}

# Rate limiting: Ensure no more than 1 request per second
def rate_limited_request(url, params):
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    time.sleep(1)  # Sleep for 1 second to comply with rate limiting
    return response

def geocode(place_name):
    url = f"{BASE_URL}/search"
    params = {
        'q': place_name,
        'format': 'json',
        'addressdetails': 1
    }
    
    response = rate_limited_request(url, params)
    
    # Parse the JSON response
    data = response.json()
    with open('data.json', 'w') as f:
        f.write(json.dumps(data, indent=2))
        
    if data:
        result = data[0]  # Take the first result
        latitude = result['lat']
        longitude = result['lon']
        address = result['address']
        
        formatted_address = (
            f"{address.get('road', '')}, "
            f"{address.get('suburb', '')}, "
            f"{address.get('city', '')}, "
            f"{address.get('state', '')}, "
            f"{address.get('country', '')}"
        ).strip(", ")
        return (latitude, longitude), formatted_address
    else:
        return None, "Place not found."

def reverse_geocode(lat, lon):
    url = f"{BASE_URL}/reverse"
    params = {
        'format': 'json',
        'lat': lat,
        'lon': lon,
        'addressdetails': 1
    }
    
    response = rate_limited_request(url, params)
    
    # Parse the JSON response
    data = response.json()
    with open('data.json', 'w') as f:
        f.write(json.dumps(data, indent=2))
    
    if 'address' in data:
        address = data['address']
        formatted_address = (
            f"{address.get('road', '')}, "
            f"{address.get('suburb', '')}, "
            f"{address.get('city', '')}, "
            f"{address.get('state', '')}, "
            f"{address.get('country', '')}"
        ).strip(", ")
        return formatted_address
    else:
        return "Address not found."

# Attribution message
def display_attribution():
    print("Geocoding data provided by Nominatim from OpenStreetMap, licensed under the ODbL.")

# Example usage
place = "Anwar Khan Modern Medical College And Hospital, Dhaka"
place = 'Delta hospital, Mirpur 1, Bangladesh'
place = 'Bangladesh Neonatal Hospital, Signboard Mor, Narayanganj, Bangladesh'
place = 'Arif Memorial Hospital, Barishal'
place = 'Apollo Hospitals Dhaka, Block: E, Plot: 81, Bashundhara R/A, Dhaka 1229'
place = 'United Hospital Limited, Dhaka'

coordinates, address = geocode(place)
print(f"Coordinates: {coordinates}")
print(f"Address: {address}")

exit()

latitude = 23.745654
longitude = 90.382433
address = reverse_geocode(latitude, longitude)
print(f"Address: {address}")

display_attribution()
