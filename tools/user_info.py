from db import supabase

def get_user_info(mobile_number):
    response = supabase.table('users').select('*').eq('mobile_number', mobile_number).single().execute()
    user = response.data
    if not user:
        return {"result": "User not found."}
    return {"result": user} 