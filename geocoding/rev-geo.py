import requests
import json 

def reverse_geocode(lat, lon):
    # Nominatim API URL
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1"

    # Send the request
    response = requests.get(url)
    response.raise_for_status()  # Check for request errors

    # Parse the JSON response
    data = response.json()
    with open('rev-geo.json','w') as f:
        f.write(json.dumps(data, indent=2))
    if 'address' in data:
        address = data['address']
        formatted_address = f"{address.get('road', '')}, {address.get('suburb', '')}, {address.get('city', '')}, {address.get('state', '')}, {address.get('country', '')}"
        return formatted_address.strip(", ")
    else:
        return "Address not found."

# Example usage
latitude = 23.7574
longitude = 90.3748
print(reverse_geocode(latitude, longitude))
