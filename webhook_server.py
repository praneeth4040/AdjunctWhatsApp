from flask import Flask, request
from message import get_text_message_input, send_message
from test_gemini import ai_response
import json

app = Flask(__name__)

def extract_user_message(data):
    try:
        return data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    except (KeyError, IndexError):
        return None

def extract_sender(data):
    try:
        return data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except (KeyError, IndexError):
        return None


