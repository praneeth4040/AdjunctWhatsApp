from db import supabase  # or from your supabase client location

def insertUser(mobile_number):
    # Check if user already exists
    response = supabase.table("users").select("id").eq("mobile_number", mobile_number).execute()
    if not response.data:  # If user does not exist
        supabase.table("users").insert({"mobile_number": mobile_number}).execute()

