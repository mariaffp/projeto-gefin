from supabase import create_client
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
admin_key = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(url, key)
supabase_admin = create_client(url, admin_key)
