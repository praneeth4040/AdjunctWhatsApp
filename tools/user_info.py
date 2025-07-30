from database import db
from typing import Dict, Any, Optional

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