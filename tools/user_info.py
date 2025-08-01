from database import db
from typing import Dict, Any, Optional
import cohere
import os
co = cohere.Client(api_key= os.getenv("COHERE_API_KEY"))



def get_user_info(mobile_number: str) -> Dict[str, Any]:
    """
    Retrieve user information from the database by mobile number.
    
    Args:
        mobile_number: The user's mobile number
        
    Returns:
        Dictionary containing the result with user data or error message
    """
    # Input validation
    if not mobile_number or not isinstance(mobile_number, str):
        return {"result": "Invalid mobile number provided."}
    
    try:
        # Get user from database
        user = db.get_user(mobile_number)
        
        if not user:
            return {"result": "User not found."}
        
        # Return user data with the new schema
        user_data = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'mobile_number': user['mobile_number'],
            'created_at': user['created_at'],
            'last_updated': user['last_updated'],
            'last_talked': user['last_talked']
        }
        
        return {"result": user_data}
        
    except Exception as e:
        print(f"Database error in get_user_info: {str(e)}")
        return {"result": "Unable to retrieve user information. Please try again later."} 


def get_user_chat_summary(mobile_number: str) -> str:
    """
    Retrieve the user's chats from the database and summarize them using Cohere's chat endpoint.
    
    Args:
        mobile_number: The user's mobile number
        
    Returns:
        String containing the summary of the chats
    """
    if not mobile_number or not isinstance(mobile_number, str):
        return "Invalid mobile number provided."
    
    try:
        chats = db.get_user_chats(mobile_number)
        if not chats:
            return "No chats found for the user."

        # Format chats into string
        chats_string = ""
        for chat in chats:
            role = "User" if chat.get("sender_type") == "user" else "Assistant"
            chats_string += f"{role}: {chat.get('message').strip()}\n"

        # Use Cohere's chat endpoint for summarization
        response = co.chat(
            message="Summarize the following conversation between a user and assistant in bullet points.",
            chat_history=[{"role": "USER", "message": chats_string}],
            temperature=0.3
        )

        return response.text if hasattr(response, "text") else "Summary could not be generated."

    except Exception as e:
        print(f"Error in get_user_chat_summary: {str(e)}")
        return "Unable to generate chat summary. Please try again later."
