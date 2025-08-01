"""
Database module for AdjunctWhatsApp using Supabase
Handles user management with PostgreSQL backend
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from supabase import create_client, Client

class DatabaseManager:
    """Manages all database operations using Supabase."""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self._init_supabase()
    
    def _init_supabase(self):
        """Initialize Supabase client."""
        try:
            # Get Supabase credentials from environment variables
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                print("Warning: SUPABASE_URL and SUPABASE_KEY environment variables not set")
                print("Database operations will not work until credentials are configured")
                return
            
            self.supabase = create_client(supabase_url, supabase_key)
            print("Supabase client initialized successfully")
            
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            self.supabase = None
    
    def is_connected(self) -> bool:
        """Check if database connection is available."""
        return self.supabase is not None
    
    # User Management Functions
    def create_user(self, mobile_number: str, name: Optional[str] = None, 
                   email: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user in the database."""
        if not self.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # Check if user already exists
            existing = self.supabase.table('users').select('id').eq('mobile_number', mobile_number).execute()
            
            if existing.data:
                return {"success": False, "error": "User already exists"}
            
            # Create new user
            user_data = {
                'mobile_number': mobile_number,
                'name': name,
                'email': email,
                'created_at': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat(),
                'last_talked': datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table('users').insert(user_data).execute()
            
            if response.data:
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "Failed to create user"}
                
        except Exception as e:
            print(f"Error creating user: {e}")
            return {"success": False, "error": str(e)}
    
    def get_user(self, mobile_number: str) -> Optional[Dict[str, Any]]:
        """Get user information by mobile number."""
        if not self.is_connected():
            return None
        
        try:
            response = self.supabase.table('users').select('*').eq('mobile_number', mobile_number).single().execute()
            return response.data if response.data else None
            
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user(self, mobile_number: str, **kwargs) -> Dict[str, Any]:
        """Update user information."""
        if not self.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # Only allow updating specific fields
            valid_fields = ['name', 'email']
            update_data = {}
            
            for field, value in kwargs.items():
                if field in valid_fields and value is not None:
                    update_data[field] = value
            
            if not update_data:
                return {"success": False, "error": "No valid fields to update"}
            
            # Add last_updated timestamp
            update_data['last_updated'] = datetime.utcnow().isoformat()
            
            response = self.supabase.table('users').update(update_data).eq('mobile_number', mobile_number).execute()
            
            if response.data:
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "User not found or update failed"}
                
        except Exception as e:
            print(f"Error updating user: {e}")
            return {"success": False, "error": str(e)}
    
    def update_last_talked(self, mobile_number: str) -> Dict[str, Any]:
        """Update the last_talked timestamp for a user."""
        if not self.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            response = self.supabase.table('users').update({
                'last_talked': datetime.utcnow().isoformat()
            }).eq('mobile_number', mobile_number).execute()
            
            if response.data:
                return {"success": True, "data": response.data[0]}
            else:
                return {"success": False, "error": "User not found"}
                
        except Exception as e:
            print(f"Error updating last_talked: {e}")
            return {"success": False, "error": str(e)}
    
    def user_exists(self, mobile_number: str) -> bool:
        """Check if a user exists."""
        return self.get_user(mobile_number) is not None
    
    def get_all_users(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all users (for admin purposes)."""
        if not self.is_connected():
            return []
        
        try:
            response = self.supabase.table('users').select('*').limit(limit).execute()
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    def ensure_user_exists(self, mobile_number: str) -> Dict[str, Any]:
        """
        Ensure a user exists in the database. If not, create them.
        This is specifically for webhook message handling.
        
        Args:
            mobile_number: The user's mobile number
            
        Returns:
            Dictionary with success status and user data
        """
        if not self.is_connected():
            return {"success": False, "error": "Database not connected"}
        
        try:
            # First, try to get existing user
            existing_user = self.get_user(mobile_number)
            
            if existing_user:
                # User exists, update last_talked timestamp
                self.update_last_talked(mobile_number)
                return {"success": True, "data": existing_user, "action": "existing_user"}
            else:
                # User doesn't exist, create new user
                create_result = self.create_user(mobile_number)
                if create_result["success"]:
                    # Get the newly created user
                    new_user = self.get_user(mobile_number)
                    return {"success": True, "data": new_user, "action": "created_user"}
                else:
                    return create_result
                    
        except Exception as e:
            print(f"Error ensuring user exists: {e}")
            return {"success": False, "error": str(e)}

    def store_message(self, mobile_number, sender_type, message):
        self.supabase.table('conversation_history').insert({
            'mobile_number': mobile_number,
            'sender_type': sender_type,
            'message': message
        }).execute()

    def get_user_chats(self, mobile_number: str) -> List[Dict[str, Any]]:
        """Get the user's chat history from the conversation_history table."""
        if not self.is_connected():
            print("Database not connected.")
            return []
    
        try:
            response = self.supabase.table('conversation_history').select('sender_type, message, created_at').eq('mobile_number', mobile_number).order(column="created_at", desc=False).execute()

            chats = response.data if response.data else []
            return chats
    
        except Exception as e:
            print(f"Error getting user chats for {mobile_number}: {e}")
            return []

# Global database instance
db = DatabaseManager()

# PostgreSQL Schema for reference:
"""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    mobile_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_talked TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_mobile_number ON users(mobile_number);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_last_talked ON users(last_talked);

-- Function to automatically update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update last_updated
CREATE TRIGGER update_users_last_updated 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_last_updated_column();
""" 