import requests
import json

def geocode(place_name):
    # Nominatim API URL
    url = f"https://nominatim.openstreetmap.org/search?q={place_name}&format=json&addressdetails=1"

    # Send the request
    response = requests.get(url)
    response.raise_for_status()  # Check for request errors

    # Parse the JSON response
    data = response.json()
    with open('geo.json', 'w') as f:
        f.write(json.dumps(data, indent=2))
        
    if data:
        result = data[0]  # Take the first result
        latitude = result['lat']
        longitude = result['lon']
        address = result['address']
        formatted_address = f"{address.get('road', '')}, {address.get('suburb', '')}, {address.get('city', '')}, {address.get('state', '')}, {address.get('country', '')}"
        return (latitude, longitude), formatted_address.strip(", ")
    else:
        return None, "Place not found."

# Example usage
place = "Anwar Khan Modern Hospital Bangladesh"
# place = 'Sheikh Hasina National Burn and Plastic Surgery Institute'
# place = 'কিডনি ফাউন্ডেশন এন্ড রিসার্চ ইনস্টিটিউট, মিরপুর, ঢাকা'
place = 'Kidney Foudation and Research Institute, Mirpur, Dhaka, Bangladesh'
place = 'Arif Memorial Hospital, Barishal, Bangladesh'

coordinates, address = geocode(place)
print(f"Coordinates: {coordinates}")
print(f"Address: {address}")
