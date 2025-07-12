from db import supabase

def store_user_memory(user_number, memory_text):
    supabase.table("user_memory").insert({
        "user_number": user_number,
        "memory_text": memory_text
    }).execute()

def get_user_memories(user_number, limit=10):
    response = supabase.table("user_memory")\
        .select("memory_text")\
        .eq("user_number", user_number)\
        .order("timestamp", desc=True)\
        .limit(limit)\
        .execute()
    return [item["memory_text"] for item in response.data] 