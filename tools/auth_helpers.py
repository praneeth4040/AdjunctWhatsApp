from whatsapp_utils.message_types import get_cta_url_message_input
from message import send_message

def prompt_gmail_authorization(mobile_number):
    oauth_url = f"http://localhost:5000/authorize?mobile_number={mobile_number}"
    payload = get_cta_url_message_input(
        recipient=mobile_number,
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Gmail_icon_%282020%29.svg/2560px-Gmail_icon_%282020%29.svg.png",
        body_text="Tap the button below to connect your Gmail account and enable email features.",
        display_text="Connect Gmail",
        url=oauth_url,
        footer_text="We need your permission to send emails on your behalf."
    )
    send_message(payload)
    return {"result": "Please connect your Gmail account to enable email features."} 