from db import supabase
from datetime import datetime, timedelta

def save_message(user_number, message, is_user):
    supabase.table("chat_history").insert({
        "user_number": user_number,
        "message": message,
        "is_user": is_user
    }).execute()

def get_recent_chat_history(user_number, limit=30, hours=4):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    response = supabase.table("chat_history")\
        .select("id, message, is_user, timestamp")\
        .eq("user_number", user_number)\
        .gte("timestamp", cutoff.isoformat())\
        .order("timestamp", desc=False)\
        .limit(limit)\
        .execute()
    return response.data

def prune_old_chat_history(user_number, keep_n=10):
    # Get the IDs of the most recent N messages
    response = supabase.table("chat_history")\
        .select("id")\
        .eq("user_number", user_number)\
        .order("timestamp", desc=True)\
        .limit(keep_n)\
        .execute()
    keep_ids = [item["id"] for item in response.data]
    if keep_ids:
        # Delete all messages not in the most recent N
        supabase.table("chat_history")\
            .eq("user_number", user_number)\
            .not_.in_("id", keep_ids)\
            .delete()\
            .execute() 