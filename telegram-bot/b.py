import requests

def fetch_donors(params):
    # Base URL of your API
    base_url = "http://localhost:3000/donor"

    try:
        # Send GET request with parameters
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            return response.json()  # Return the list of donors
        else:
            return {
                "success": False,
                "error": f"Failed with status code {response.status_code}",
                "details": response.text
            }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


params = {
    'telegramUsername': 'john_doe',
    'chatPlatform': 'telegram'
}
# Example usage
donors = fetch_donors(params)
print(donors)
