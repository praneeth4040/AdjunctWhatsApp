import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

def send_email_on_behalf(user_email, google_token, recipient_email, subject, body):
    if not google_token:
        return {'result': 'NO_TOKEN'}

    creds = Credentials.from_authorized_user_info(google_token, SCOPES)
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(body)
    message['to'] = recipient_email
    message['from'] = user_email
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw}
    try:
        sent_message = service.users().messages().send(userId='me', body=message_body).execute()
        return {'result': f"Email sent to {recipient_email}. Message ID: {sent_message['id']}"}
    except Exception as e:
        return {'result': f"Failed to send email: {e}"}
