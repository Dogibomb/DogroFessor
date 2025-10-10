from api_key import SUPABASE_URL, SUPABASE_KEY
from supabase import create_client
from datetime import datetime

supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_message(username, message):
    supabase_client.table("messages").insert({
        "username": username,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }).execute()

def load_messages(limit=10):
    response = supabase_client.table("messages") \
        .select("*") \
        .order("id", desc=True) \
        .limit(limit) \
        .execute()
    return response.data[::-1]  
