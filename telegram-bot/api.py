import requests
import json
from typing import Dict, Any, Optional
from utils import *
localhost_backend_url = "http://localhost:3000"
remote_backend_url = "https://delta-blood-bot-backend.onrender.com"

base_url = remote_backend_url

# if ENV == 'development':
#     base_url = localhost_backend_url

class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            if response.status_code == 200:
                return response.json()
            return {
                "success": False,
                "error": f"Failed with status code {response.status_code}",
                "details": response.text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                data=json.dumps(data) if data else None,
                params=params
            )
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }

    def getX(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        return self._make_request("GET", endpoint, params=params)

    def postX(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._make_request("POST", endpoint, data=data)

    def putX(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        return self._make_request("PUT", endpoint, data=data)

    def deleteX(self, endpoint: str) -> Dict[str, Any]:
        return self._make_request("DELETE", endpoint)

api = ApiClient(base_url)

def create_donor(payload: Dict) -> Dict[str, Any]:
    return api.postX("donor", payload)

def fetch_donors(params: Optional[Dict] = None) -> Dict[str, Any]:
    return api.getX("donor", params)

def update_donor(donor_id: str, payload: Dict) -> Dict[str, Any]:
    return api.putX(f"donor/{donor_id}", payload)

def create_bloodrequest(payload: Dict) -> Dict[str, Any]:
    return api.postX("bloodrequest", payload)

def find_matching_donors(bloodrequest_id: str) -> Dict[str, Any]:
    return api.getX(f"donor/match/{bloodrequest_id}", {})

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

# br_payload = {
#         "messageText": "Urgent blood needed",
#         "bloodGroup": "A+",
#         "bagsNeeded": 2,
#         "patientName": "John Doe",
#         "patientGender": "male",
#         "patientAgeGroup": "adult",
#         "condition": "surgery",
#         "location": "Dhaka",
#         "hospitalName": "Square Hospital",
#         "locationMarkers": ["Dhaka", "Banani"],
#         "probableDay": "2024-03-20",
#         "probableTime": "10:00 AM",
#         "transportation": "Y",
#         "allowance": "Y",
#         "sourceTelegramChatId": "123456789",
#         "contacts": [
#             {
#                 "name": "Jane Doe",
#                 "numbers": ["+8801712345678", "+8801812345678"],
#                 "relationWithPatient": "sister"
#             },
#             {
#                 "name": "John Smith",
#                 "numbers": ["+8801612345678"],
#                 "relationWithPatient": "friend"
#             }
#         ]
#     }

# br_payload = {'messageText': '#URGENT\nBlood Needed\nরক্তের গ্রুপ: B-\nস্থান :BRB Hospital,Panthapath\nযোগাযোগ:01877621398\nসময়: আজকে বিকেলের মধ্যে(রোগীর সিচুয়েশন ক্রিটিক্য       যাল)', 'bloodGroup': 'B-', 'bagsNeeded': None, 'patientName': '', 'patientGender': '', 'patientAgeGroup': '', 'condition': 'Critical situation', 'location': 'BRB Hospital,Panthapath', 'hospitalName': 'BRB Hospital', 'locationMarkers': ['Panthapath'], 'probableDay': 'today', 'probableTime': 'in 0 hours', 'transportation': '', 'allowance': '', 'contacts': [{'name': '', 'numbers': ['01877621398'], 'relationWithPatient': ''}]}

# create_bloodrequest(br_payload)

# print(find_matching_donors("6711835db65b4ec709f2efa3"))