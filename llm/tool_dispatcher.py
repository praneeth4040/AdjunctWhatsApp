from tools.reminder import schedule_whatsapp_reminder
from tools.emails import send_email_on_behalf, receive_emails
from tools.user_info import get_user_info
from tools.auth_helpers import prompt_gmail_authorization
from chat_db import get_recent_chat_history

def dispatch_tool_call(name, args, recipient):
    print(f"Tool called: {name} with args: {args}")
    """
    Dispatches the tool call to the correct function based on name.
    Args:
        name (str): The name of the function/tool to call.
        args (dict): Arguments for the function.
    Returns:
        dict: The result from the tool function.
    """
    if name == "set_reminder":
        return schedule_whatsapp_reminder(recipient, args["event"], args["time_str"])
    elif name == "send_email":
        google_token = args.get("google_token")
        if not google_token:
            return prompt_gmail_authorization(recipient)
        return send_email_on_behalf(
            user_email=args["user_email"],
            google_token=google_token,
            recipient_email=args["recipient_email"],
            subject=args["subject"],
            body=args["body"]
        )
    elif name == "receive_emails":
        google_token = args.get("google_token")
        if not google_token:
            return prompt_gmail_authorization(recipient)
        max_results = args.get("max_results", 5)
        return receive_emails(
            user_email=args["user_email"],
            google_token=google_token,
            max_results=max_results
        )
    elif name == "get_user_info":
        # Always inject the sender's mobile number
        return get_user_info(recipient)
    elif name == "get_chat_history":
        # Use recipient as user_number, allow limit and hours as optional args
        limit = args.get("limit", 30)
        hours = args.get("hours", 4)
        history = get_recent_chat_history(recipient, limit=limit, hours=hours)
        return {"result": history}
    else:
        return {"result": f"Unknown tool: {name}"} 