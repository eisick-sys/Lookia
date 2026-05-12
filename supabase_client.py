# supabase_client.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://pkojtqwatctncuerilub.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_client: Client = None
_service_client: Client = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


def get_supabase_service() -> Client:
    global _service_client
    if _service_client is None:
        if not SUPABASE_SERVICE_KEY:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY no está definida en .env")
        _service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _service_client


def get_supabase_for_user(access_token: str) -> Client:
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.auth.set_session(access_token, "")
    return client