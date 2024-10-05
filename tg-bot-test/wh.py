# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

## HELP DOCS
# https://console.twilio.com/
# https://www.twilio.com/docs/whatsapp/quickstart


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

message = client.messages.create(
    to="whatsapp:+8801531949133",
    from_="whatsapp:+14155238886",
    body="Hello there!",
)

print(message.body)