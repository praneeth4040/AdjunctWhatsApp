from tools.reminder import schedule_whatsapp_reminder
from tools.emails import send_email_on_behalf, receive_emails
from tools.user_info import get_user_info
from tools.auth_helpers import prompt_google_authorization
from app import search_google
from typing import Dict, Any, Optional

def dispatch_tool_call(name: str, args: Dict[str, Any], recipient: str) -> Dict[str, Any]:
    """
    Dispatch tool calls to the appropriate function based on the tool name.
    
    Args:
        name: The name of the tool to call
        args: Arguments for the tool call
        recipient: The recipient's identifier (usually mobile number)
        
    Returns:
        Dictionary containing the result of the tool call
    """
    # Input validation
    if not name or not isinstance(name, str):
        return {"result": "Invalid tool name provided."}
    
    if not isinstance(args, dict):
        return {"result": "Invalid arguments provided."}
    
    if not recipient or not isinstance(recipient, str):
        return {"result": "Invalid recipient provided."}
    
    # Sanitize inputs
    name = name.strip().lower()
    
    try:
        print(f"Tool called: {name} for recipient: {recipient}")
        
        if name == "set_reminder":
            # Validate required arguments
            if "event" not in args or "time_str" not in args:
                return {"result": "Missing required arguments: event and time_str"}
            
            event = args.get("event", "")
            time_str = args.get("time_str", "")
            
            if not event or not time_str:
                return {"result": "Event and time_str cannot be empty"}
            
            return schedule_whatsapp_reminder(recipient, event, time_str)
        
        elif name == "send_email":
            # Validate required arguments
            required_fields = ["user_email", "recipient_email", "subject", "body"]
            for field in required_fields:
                if field not in args:
                    return {"result": f"Missing required argument: {field}"}
            
            google_token = args.get("google_token")
            if not google_token:
                return prompt_google_authorization(recipient)
            
            return send_email_on_behalf(
                user_email=args["user_email"],
                google_token=google_token,
                recipient_email=args["recipient_email"],
                subject=args["subject"],
                body=args["body"]
            )
        
        elif name == "receive_emails":
            # Validate required arguments
            if "user_email" not in args:
                return {"result": "Missing required argument: user_email"}
            
            google_token = args.get("google_token")
            if not google_token:
                return prompt_google_authorization(recipient)
            
            max_results = args.get("max_results", 5)
            # Validate max_results is a reasonable number
            if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
                max_results = 5
            
            return receive_emails(
                user_email=args["user_email"],
                google_token=google_token,
                max_results=max_results
            )
        
        elif name == "get_user_info":
            return get_user_info(recipient)
        
        elif name == "web_search":
            query = args.get("query", "")
            if not query or not isinstance(query, str) or len(query.strip()) == 0:
                return {"result": "Search query is required and cannot be empty."}
            
            # Sanitize query
            query = query.strip()
            if len(query) > 500:  # Limit query length
                query = query[:500]
            
            return {"result": search_google(query)}
        
        elif name == "prompt_google_authorization":
            return prompt_google_authorization(recipient)
        
        else:
            return {"result": f"Unknown tool: {name}. Available tools: set_reminder, send_email, receive_emails, get_user_info, web_search, prompt_google_authorization"}
    
    except Exception as e:
        print(f"Error in tool dispatcher for {name}: {str(e)}")
        return {"result": f"An error occurred while processing your request. Please try again."}
