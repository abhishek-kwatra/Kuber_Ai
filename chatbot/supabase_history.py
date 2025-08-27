# chatbot/supabase_history.py
import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
from langchain_core.chat_history import BaseChatMessageHistory

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Please set SUPABASE_URL and SUPABASE_KEY in environment")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Declaring Class to wrap all the database function
class SupabaseChatHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self.session_id = session_id

    def add_message(self, message: dict):
        # message: {"type": "human"/"ai", "content": "..."} Syntax of message in table 
        supabase.table("chat_history").insert({
            "session_id": self.session_id,
            "role": message["type"],
            "content": message["content"],
            "created_at": datetime.utcnow().isoformat()
        }).execute()

    @property
    def messages(self):
        res = supabase.table("chat_history") \
            .select("*") \
            .eq("session_id", self.session_id) \
            .order("created_at").execute()

        rows = res.data or []
        return [{"role": r["role"], "content": r["content"], "created_at": r["created_at"]} for r in rows]

    def clear(self):
        supabase.table("chat_history").delete().eq("session_id", self.session_id).execute()
        
    def add_investment(self, name: str, phone: str):
        # Adds an investment record to the gold_investors table.
        data = {
            "session_id": self.session_id,
            "name": name,
            "phone": phone,
            "created_at": datetime.utcnow().isoformat()
        }
        supabase.table("gold_investors").insert(data).execute() 
        
    def clear(self):
        supabase.table("chat_history").delete().eq("session_id", self.session_id).execute()
