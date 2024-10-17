import requests
import json

localhost_backend_url = "http://localhost:3000"
remote_backend_url = "https://delta-blood-bot-backend.onrender.com"

api_base = localhost_backend_url

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

def update_donor(payload):
    donor_id = payload.get('donor_id')
    url = f"{api_base}/donor/{donor_id}"  # Replace with your actual API endpoint
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        
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
# donor_payload = {
#     "name": "John Doe 4",
#     "firstName": "John",
#     "lastName": "Doe",
#     "chatPlatform": "telegram",
#     "telegramUsername": "john_doe",
#     "discordUserId": None,
#     "telegramChatId": "123456789",
# }

# # Calling the function
# response = create_donor(donor_payload)
# print(response)


# params = {
#     'telegramUsername': 'john_doe',
#     'chatPlatform': 'telegram'
# }
# # Example usage
# donors = fetch_donors(params)
# print(donors)

# update_payload = {
#     "donor_id": "6710c6fbfa9ca04f6fea2646", 
#     "isNotificationDisabled": True
# }

# result = update_donor(update_payload)
# print(result)
