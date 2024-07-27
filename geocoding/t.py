import requests
import json
import time

from util import * 

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

    # with open('data.json', 'w') as f:
    #     f.write(json.dumps(data, indent=2))

    return data
        
    # if data:
    #     result = data[0]  # Take the first result
    #     latitude = result['lat']
    #     longitude = result['lon']
    #     address = result['address']
        
    #     formatted_address = (
    #         f"{address.get('road', '')}, "
    #         f"{address.get('suburb', '')}, "
    #         f"{address.get('city', '')}, "
    #         f"{address.get('state', '')}, "
    #         f"{address.get('country', '')}"
    #     ).strip(", ")
    #     return (latitude, longitude), formatted_address
    # else:
    #     return None, "Place not found."

data = read_json('data/private-hospitals-bd.json')

print(len(data))

ndata = []

i = 0
for d in data:
    print(i)
    name = ', '.join([d['name'], d['upazila'], d['district']])
    # print(name)
    d['location_detail'] = geocode(name)
    ndata.append(d)
    if (i%20 == 0):
        write_json('processed.json',ndata)
        print(f'written for {i}')
    i += 1


