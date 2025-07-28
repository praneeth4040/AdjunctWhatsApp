from google import genai
from google.genai import types
from llm.tool_dispatcher import dispatch_tool_call
from gemini_prompt import SYSTEM_PROMPT
from chat_db import get_recent_chat_history, save_message
from auth_helpers import prompt_google_authorization

# Define function declarations for tools
reminder_function = {
    "name": "set_reminder",
    "description": "Set a reminder for the user. Supports absolute and relative times.",
    "parameters": {
        "type": "object",
        "properties": {
            "event": {
                "type": "string",
                "description": "The event to remind the user about."
            },
            "time_str": {
                "type": "string",
                "description": "When to remind the user, e.g., 'in 10 minutes', 'at 5:00pm'."
            }
        },
        "required": ["event", "time_str"]
    }
}

send_email_function = {
    "name": "send_email",
    "description": "Send an email on behalf of the user using their connected Gmail account.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_email": {
                "type": "string",
                "description": "The sender's Gmail address."
            },
            "google_token": {
                "type": "object",
                "description": "The user's Google OAuth token as a JSON object.",
                "nullable": True
            },
            "recipient_email": {
                "type": "string",
                "description": "The email address to send to."
            },
            "subject": {
                "type": "string",
                "description": "The subject of the email."
            },
            "body": {
                "type": "string",
                "description": "The body content of the email."
            }
        },
        "required": ["recipient_email", "subject", "body"]
    }
}

get_user_info_function = {
    "name": "get_user_info",
    "description": "Get user details from the database by mobile number.",
    "parameters": {
        "type": "object",
        "properties": {
            "mobile_number": {
                "type": "string",
                "description": "The user's mobile number (provided by the system)."
            }
        }
    }
}

receive_emails_function = {
    "name": "receive_emails",
    "description": "Fetch the latest emails from the user's Gmail inbox.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_email": {
                "type": "string",
                "description": "The user's Gmail address."
            },
            "google_token": {
                "type": "object",
                "description": "The user's Google OAuth token as a JSON object.",
                "nullable": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of emails to fetch (default 5).",
                "default": 5
            }
        },
        "required": ["user_email", "google_token"]
    }
}

web_search_function = {
    "name": "web_search",
    "description": "Perform a web search and return a summary with relevant links.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up on the web."
            }
        },
        "required": ["query"]
    }
}

google_authorisation_function = {
    "name": "prompt_google_authorization",
    "description": "Prompt the user to authorize access to their Google account for Gmail features.",
    "parameters": {
        "type": "object",
        "properties": {
            "mobile_number": {
                "type": "string",
                "description": "The user's mobile number for sending the authorization message."
            }
        },
        "required": ["mobile_number"]
    }
}


# Gemini tool configuration
client = genai.Client()
tools = types.Tool(function_declarations=[
    reminder_function,
    send_email_function,
    get_user_info_function,
    receive_emails_function,
    web_search_function ,
    google_authorization_function# ✅ include web search here
])
config = types.GenerateContentConfig(tools=[tools])

# AI response generation
def ai_response(recipient, user_message):
    history = get_recent_chat_history(recipient, limit=50, hours=4) or []
    history_lines = []

    for msg in history:
        prefix = "User:" if msg.get("is_user") else "Bot:"
        history_lines.append(f"{prefix} {msg.get('message')}")

    context = [SYSTEM_PROMPT] + history_lines + [f"User: {user_message}"]

    while True:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=context,
            config=config,
        )
        part = response.candidates[0].content.parts[0]

        if hasattr(part, "function_call") and part.function_call:
            function_call = part.function_call
            tool_call_msg = f"Tool call: {function_call.name}({function_call.args})"
            print(tool_call_msg)
            context.append(tool_call_msg)

            result = dispatch_tool_call(function_call.name, function_call.args, recipient)
            tool_result_msg = f"Tool result: {result['result']}"
            print(tool_result_msg)
            context.append(tool_result_msg)
        else:
            return response.text
