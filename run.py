from re import M
from flask import Flask, request, abort, jsonify, session, redirect, url_for
from webhook_server import extract_user_message, extract_sender ,extract_media_info
from test_gemini import ai_response
from message import send_message, send_read_and_typing_indicator
from whatsapp_utils.message_types import get_text_message_input
from gemini_prompt import SYSTEM_PROMPT
from database import db
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
            # Validate JSON payload
            if not request.is_json:
                return jsonify({'error': 'Invalid content type, JSON required.'}), 400
            data = request.get_json(force=True, silent=True)
            if not data:
                return jsonify({'error': 'Empty or invalid JSON payload.'}), 400
            # mark message as read and send typing status
            send_read_and_typing_indicator(data["entry"][0]["changes"][0]["value"]["messages"][0]["id"])

            # extract message and sender and media info
            msg = extract_user_message(data)
            sender = extract_sender(data)
            media_info = extract_media_info(data["entry"][0]["changes"][0]["value"]["messages"][0])
            if (not msg and not media_info )or not sender :
                print("Missing message or sender in payload.")
                return jsonify({'error': 'Missing message or sender in payload.'}), 400
            if media_info:
                print("Media message detected.")
                send_message(get_text_message_input(sender, "I'm sorry, I can't process media messages yet."))
                return jsonify({'result': media_info}), 200
            # Ensure user exists in database (create if not exists)
            user_result = db.ensure_user_exists(sender)
            if not user_result["success"]:
                print(f"Database error for user {sender}: {user_result.get('error', 'Unknown error')}")
                # Continue with AI response even if database fails
            else:
                action = user_result.get("action", "unknown")
                if action == "created_user":
                    print(f"New user created: {sender}")
                elif action == "existing_user":
                    print(f"Existing user updated: {sender}")

            # Call AI response
            ai_result = ai_response(sender, msg)
            db.store_message(sender, "user", msg)
            db.store_message(sender, "bot", ai_result)
            
            # send message to user
            send_message(get_text_message_input(sender, ai_result))
            return jsonify({'result': ai_result}), 200
        except Exception as e:
            # Log error securely (do not leak sensitive info)
            print(f"Webhook error: {str(e)}")
            return jsonify({'error': 'Internal server error.'}), 500

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
        include_granted_scopes='true',
        prompt='consent'
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

    # Update user in database with Google OAuth info
    update_result = db.update_user(mobile_number, name=name, email=email)
    if update_result["success"]:
        print(f"User {mobile_number} updated with Google OAuth info")
    else:
        print(f"Failed to update user {mobile_number}: {update_result.get('error', 'Unknown error')}")

    return 'Authorization complete! You can close this window.'

@app.route('/healthcheck')
def healthcheck():
    try:
        return "the server is active"
    except Exception as e:
        return e

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
