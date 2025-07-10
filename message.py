import json
from dotenv import load_dotenv
import os
import requests
import aiohttp
import asyncio

# --------------------------------------------------------------
# Load environment variables
# --------------------------------------------------------------

load_dotenv()
ACCESS_TOKEN = "EAAKWB7fRXUIBPJRfpRmizFmzFBAfZBPZBEEJZCHvUZA53SjoQL5skyKMZAlOZA9cebIuyQvdxUhFChMidTzHjRuchHZBmlvHsiZAZCFiIg0ZA6yCfHMvgvZAM13dSylGtBLJLZCMLtZB0nbm1hzo9bC5amBMShfnLl00ZCuFiOWPdoRZCTCMjdV9zOdNHCJz9lZCjRQAawZDZD"
RECIPIENT_WAID = "919121314837"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

print(repr(ACCESS_TOKEN))
print(repr(RECIPIENT_WAID))
print(repr(PHONE_NUMBER_ID))
print(repr(VERSION))

# --------------------------------------------------------------
# Send a template WhatsApp message
# --------------------------------------------------------------


def send_whatsapp_message():
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_WAID,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }
    response = requests.post(url, headers=headers, json=data)
    return response


# Call the function
#response = send_whatsapp_message()
#print(response.status_code)
#print(response.json())

def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"

    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        print("Status:", response.status_code)
        print("Content-type:", response.headers["content-type"])
        print("Body:", response.text)
        return response
    else:
        print(response.status_code)
        print(response.text)
        return response


data = get_text_message_input(
    recipient=RECIPIENT_WAID, text="Hello, this is a test message."
)

response = send_message(data)
