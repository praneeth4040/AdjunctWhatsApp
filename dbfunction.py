from db import supabase  # or from your supabase client location

def insertUser(mobile_number):
    # Check if user already exists
    response = supabase.table("users").select("id").eq("mobile_number", mobile_number).execute()
    if not response.data:  # If user does not exist
        supabase.table("users").insert({"mobile_number": mobile_number}).execute()

def save_message(user_number, message, is_user):
    supabase.table("chat_history").insert({
        "user_number": user_number,
        "message": message,
        "is_user": is_user
    }).execute()

def get_chat_history(user_number, limit=10):
    response = supabase.table("chat_history")\
        .select("message, is_user")\
        .eq("user_number", user_number)\
        .order("timestamp", desc=False)\
        .limit(limit)\
        .execute()
    return response.data 