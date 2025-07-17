from db import supabase  # or from your supabase client location

def insertUser(mobile_number):
    # Check if user already exists
    response = supabase.table("users").select("id").eq("mobile_number", mobile_number).execute()
    if not response.data:  # If user does not exist
        supabase.table("users").insert({"mobile_number": mobile_number}).execute()


def updateUser(mobile_number, google_token, name=None, email=None):
    # Prepare the update data
    update_data = {"google_token": google_token}
    if name:
        update_data["name"] = name
    if email:
        update_data["email"] = email
    # Update the user by mobile_number
    supabase.table("users").update(update_data).eq("mobile_number", mobile_number).execute()

