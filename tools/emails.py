import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from typing import Dict, Any, List, Optional
import re

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]   

def validate_email(email: str) -> bool:
    """
    Basic email validation using regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email format is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def send_email_on_behalf(user_email: str, google_token: Dict[str, Any], 
                        recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Send an email on behalf of the user using their connected Gmail account.
    
    Args:
        user_email: The sender's Gmail address
        google_token: The user's Google OAuth token as a JSON object
        recipient_email: The email address to send to
        subject: The subject of the email
        body: The body content of the email
        
    Returns:
        Dictionary containing the result message
    """
    # Input validation
    if not google_token:
        return {'result': 'Google authorization required. Please connect your Google account first.'}
    
    if not validate_email(user_email):
        return {'result': 'Invalid sender email address provided.'}
    
    if not validate_email(recipient_email):
        return {'result': 'Invalid recipient email address provided.'}
    
    if not subject or not isinstance(subject, str) or len(subject.strip()) == 0:
        return {'result': 'Email subject is required.'}
    
    if not body or not isinstance(body, str) or len(body.strip()) == 0:
        return {'result': 'Email body is required.'}
    
    # Sanitize inputs
    subject = subject.strip()
    body = body.strip()
    
    try:
        creds = Credentials.from_authorized_user_info(google_token, SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        message = MIMEText(body)
        message['to'] = recipient_email
        message['from'] = user_email
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {'raw': raw}
        
        sent_message = service.users().messages().send(userId='me', body=message_body).execute()
        return {'result': f"Email sent successfully to {recipient_email}"}
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {'result': 'Failed to send email. Please check your Google account connection and try again.'}

def receive_emails(user_email: str, google_token: Dict[str, Any], max_results: int = 5) -> Dict[str, Any]:
    """
    Fetches the latest emails from the user's Gmail inbox.
    
    Args:
        user_email: The user's Gmail address
        google_token: The user's Google OAuth token as a JSON object
        max_results: Maximum number of emails to fetch (default 5, max 20)
        
    Returns:
        Dictionary containing the result with list of emails or error message
    """
    # Input validation
    if not google_token:
        return {'result': 'Google authorization required. Please connect your Google account first.'}
    
    if not validate_email(user_email):
        return {'result': 'Invalid email address provided.'}
    
    if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
        max_results = 5  # Default to 5 if invalid

    try:
        creds = Credentials.from_authorized_user_info(google_token, SCOPES)
        service = build('gmail', 'v1', credentials=creds)

        results = service.users().messages().list(
            userId='me', 
            maxResults=max_results, 
            labelIds=['INBOX']
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            try:
                msg_data = service.users().messages().get(
                    userId='me', 
                    id=msg['id'], 
                    format='metadata', 
                    metadataHeaders=['Subject', 'From']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
                subject = headers.get('Subject', '(No Subject)')
                sender = headers.get('From', '(Unknown Sender)')
                snippet = msg_data.get('snippet', '')
                
                emails.append({
                    'subject': subject, 
                    'from': sender, 
                    'snippet': snippet
                })
                
            except Exception as msg_error:
                print(f"Error fetching individual email: {str(msg_error)}")
                continue  # Skip this email and continue with others
        
        if not emails:
            return {'result': 'No emails found in your inbox.'}
            
        return {'result': emails}
        
    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return {'result': 'Failed to fetch emails. Please check your Google account connection and try again.'}
