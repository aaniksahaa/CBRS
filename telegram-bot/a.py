import requests
import json

localhost_backend_url = "http://localhost:3000"
remote_backend_url = "https://delta-blood-bot-backend.onrender.com"

api_base = remote_backend_url

def create_donor(payload):
    url = f"{api_base}/donor"  # Replace with your actual API endpoint
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.json()  # The success response from your API
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

# Example payload for creating a donor
donor_payload = {
    "name": "John Doe 4",
    "firstName": "John",
    "lastName": "Doe",
    "chatPlatform": "telegram",
    "telegramUsername": "john_doe",
    "discordUserId": None,
    "telegramChatId": "123456789",
    # "latitude": 37.7749,
    # "longitude": -122.4194,
    # "lastDonated": "2023-08-12T00:00:00Z",  # Example of ISO formatted date
    # "bloodGroup": "O+",
    # "isNotificationDisabled": False
}

# Calling the function
response = create_donor(donor_payload)
print(response)

print(2+2)
