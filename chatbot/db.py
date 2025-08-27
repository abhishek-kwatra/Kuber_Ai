import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase connection
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# ✅ Create a new session (if not exists)
def create_session(session_id: str, name, phone):
    existing = supabase.table("sessions").select("*").eq("session_id", session_id).execute()
    if not existing.data:
        supabase.table("sessions").insert({
            "session_id": session_id,
            "name":name,
            "phone":phone
        }).execute()
    return session_id


# ✅ Save a single message
def save_message(session_id: str, role: str, content: str):
    supabase.table("messages").insert({
        "session_id": session_id,
        "role": role,
        "content": content
    }).execute()


# ✅ Get all messages for a session
def get_messages(session_id: str):
    response = supabase.table("messages").select("*").eq("session_id", session_id).order("id").execute()
    return response.data


# ✅ Delete session + its messages
def delete_session(session_id: str):
    supabase.table("messages").delete().eq("session_id", session_id).execute()
    supabase.table("sessions").delete().eq("session_id", session_id).execute()
