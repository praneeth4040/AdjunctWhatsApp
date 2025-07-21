from google import genai
from google.genai import types
from llm.tool_dispatcher import dispatch_tool_call
from gemini_prompt import SYSTEM_PROMPT
from chat_db import get_recent_chat_history, save_message

# Define the function declaration for the model
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
    "description": "Send an email on behalf of the user using their connected Gmail account. Always use the user's email and google_token obtained from the get_user_info tool. Always generate the subject and body from the user's request unless otherwise specified. If google_token is missing, this tool will return a Gmail authorization URL for the user to connect their account. If the token is present, proceed to send the email. Only ask the user for more details if the request is truly ambiguous or missing essential information.",
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
                "description": "The subject of the email.Generate the subject of email based on the context given by the user"
            },
            "body": {
                "type": "string",
                "description": "The body content of the email.Generate the body of the email based on the given context by the user"
            }
        },
        "required": ["recipient_email", "subject", "body"]
    }
}

get_user_info_function = {
    "name": "get_user_info",
    "description": "Get user details from the database by mobile number. This tool returns the user's name, email, google_token (for Gmail access), and other available user information. The system will automatically provide the sender's mobile number; you do not need to ask the user for it.",
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
    "description": "Fetch the latest emails from the user's Gmail inbox. Always use the user's email and google_token obtained from the get_user_info tool. Returns a list of emails with subject, sender, and snippet.",
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

# Remove get_chat_history_function from tool declarations
client = genai.Client()
tools = types.Tool(function_declarations=[reminder_function, send_email_function, get_user_info_function, receive_emails_function])
config = types.GenerateContentConfig(tools=[tools])

# Send request with function declarations
# user_message should be a list of strings (full context)
def ai_response(recipient, user_message):
    # Fetch recent chat history and build context
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