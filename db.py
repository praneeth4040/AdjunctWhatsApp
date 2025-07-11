from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
sUrl=os.getenv("supabaseUrl")

sKey=os.getenv("supabaseKey")

supabase=create_client(sUrl,sKey)

