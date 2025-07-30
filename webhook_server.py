from flask import Flask, request
from whatsapp_utils.message_types import get_text_message_input
from message import send_message
from test_gemini import ai_response
import json
import requests

app = Flask(__name__)

def extract_user_message(data):
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        msg_type = message.get("type")

        if msg_type == "text":
            return message["text"]["body"]

        elif msg_type == "interactive":
            # Could be a button or list reply
            interactive = message.get("interactive", {})
            if interactive.get("type") == "button_reply":
                return interactive["button_reply"]["title"]
            elif interactive.get("type") == "list_reply":
                return interactive["list_reply"]["title"]
        
        # For all other types (image, audio, etc), return None
        return None
    except (KeyError, IndexError):
        return None


def extract_sender(data):
    try:
        return data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except (KeyError, IndexError):
        return None

def extract_media_info(message: dict):
    print("the media message is ",message)
    media_types = ["image", "document", "voice"]
    
    if "type" not in message or message["type"] not in media_types:
        return None  # Not a media message

    media_type = message["type"]
    media_data = message.get(media_type)

    if not media_data:
        return None  # Malformed media block

    return {
        "media_type": media_type,
        "id": media_data.get("id"),
        "mime_type": media_data.get("mime_type"),
        "sha256": media_data.get("sha256"),
        "caption": media_data.get("caption", ""),  # optional
        "from": message.get("from"),
        "timestamp": message.get("timestamp"),
    }

