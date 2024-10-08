import requests

url = 'http://localhost:8080/send_message'
data = {
    'chat_id': '1133364176',  # Replace with actual chat_id
    'message': 'Hello from external trigger!'
}

response = requests.post(url, json=data)

print(response.text)  # Output: Message sent to chat 123456789
