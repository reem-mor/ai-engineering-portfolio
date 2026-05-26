from supabase import Client, create_client

from app.core.config import settings


def get_supabase_client() -> Client:
    if not settings.database_enabled:
        raise ValueError("Database is disabled.")
    if not settings.supabase_url:
        raise ValueError("SUPABASE_URL is required.")
    if not settings.supabase_service_role_key:
        raise ValueError("SUPABASE_SERVICE_ROLE_KEY is required.")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
