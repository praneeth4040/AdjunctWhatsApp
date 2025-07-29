from flask import Flask, request, abort, jsonify, session, redirect, url_for
from webhook_server import extract_user_message, extract_sender
from test_gemini import ai_response
from message import send_message
from whatsapp_utils.message_types import get_text_message_input
from dbfunction import insertUser, updateUser
from chat_db import save_message, get_recent_chat_history
from memory_db import store_user_memory, get_user_memories
from gemini_prompt import SYSTEM_PROMPT
import os
from google_auth_oauthlib.flow import Flow
import json
from googleapiclient.discovery import build
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

VERIFY_TOKEN = 'yoyo'  # Change this to your actual verify token

app.secret_key = 'your_secret_key'  # Needed for session
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), 'credits.json')
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',        # Read Gmail messages
    'https://www.googleapis.com/auth/gmail.send',            # Send Gmail messages
    'https://www.googleapis.com/auth/gmail.modify',          # Read and modify Gmail (mark as read, delete, etc.)
    'https://www.googleapis.com/auth/gmail.labels',          # Manage Gmail labels
    'https://www.googleapis.com/auth/userinfo.email',        # Get user's email address
    'https://www.googleapis.com/auth/userinfo.profile',      # Get user's basic profile info (name, picture)
    'openid'                                                 # For OpenID Connect (recommended for user identity)
]

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print('WEBHOOK_VERIFIED')
            return challenge, 200
        else:
            return 'Verification token mismatch', 403
    elif request.method == 'POST':
        try:
            msg = extract_user_message(request.json)
            sender = extract_sender(request.json)
            prnt(sender)
            insertUser(sender)
            save_message(sender, msg, True)
            # Only pass the current message and sender to ai_response
            ai_reponse = ai_response(sender, msg)
            save_message(sender, ai_reponse, False)
            if isinstance(ai_reponse, dict):
                message_text = str(ai_reponse.get("result", str(ai_reponse)))
            else:
                message_text = str(ai_reponse)
            send_message(get_text_message_input(sender, message_text))
        except Exception as e:
            print(e)
        return jsonify({'status': 'success'}), 200

@app.route('/authorize')
def authorize():
    mobile_number = request.args.get('mobile_number')
    if mobile_number:
        session['mobile_number'] = mobile_number
    # Debug print statements to check credentials file path and contents
    print("CREDENTIALS_FILE path:", CREDENTIALS_FILE)
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            creds_content = f.read()
            print("CREDENTIALS_FILE contents:", creds_content)
    except Exception as e:
        print("Error reading CREDENTIALS_FILE:", e)
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True, _scheme='https')
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True, _scheme='https')
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Fetch user info from Google
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()
    email = user_info['email']
    name = user_info.get('name', '')

    # Get mobile_number from session
    mobile_number = session.get('mobile_number')
    if not mobile_number:
        return 'Mobile number not found in session. Please start the OAuth flow from WhatsApp.', 400

    # Update user in DB
    updateUser(mobile_number, json.loads(credentials.to_json()), name, email)

    return 'Authorization complete! You can close this window.'

@app.route('/healthcheck')
def healthcheck():
    try:
        return "the server is active"
    except Exception as e:
        return e

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
