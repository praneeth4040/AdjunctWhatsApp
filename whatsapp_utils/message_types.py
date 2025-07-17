import os

def get_text_message_input(recipient, text):
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }


def get_cta_url_message_input(
    recipient,
    image_url,
    body_text,
    display_text,
    url,
    footer_text=None
):
    """
    Constructs a WhatsApp CTA URL interactive message payload.
    """
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "interactive",
        "interactive": {
            "type": "cta_url",
            "header": {
                "type": "image",
                "image": {
                    "link": image_url
                }
            },
            "body": {
                "text": body_text
            },
            "action": {
                "name": "cta_url",
                "parameters": {
                    "display_text": display_text,
                    "url": url
                }
            }
        }
    }
    if footer_text:
        payload["interactive"]["footer"] = {"text": footer_text}
    return payload 