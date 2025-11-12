import os, json, pathlib
from typing import Any, Dict, Optional
from supabase import create_client, Client

def _env(k: str, default: Optional[str]=None) -> Optional[str]:
    v = os.getenv(k, default)
    return v

def get_client() -> Optional[Client]:
    url = _env("SUPABASE_URL")
    key = _env("SUPABASE_SERVICE_ROLE_KEY")
    if not (url and key):
        return None
    return create_client(url, key)

def upsert(table: str, data: Dict[str, Any]):
    sb = get_client()
    if not sb: return None
    return sb.table(table).upsert(data).execute()

def insert(table: str, data: Dict[str, Any]):
    sb = get_client()
    if not sb: return None
    return sb.table(table).insert(data).execute()

def upload_artifact(local_path: str, remote_path: str) -> Optional[str]:
    sb = get_client()
    bucket = os.getenv("SUPABASE_STORAGE_BUCKET","evidence")
    if not sb: return None
    with open(local_path, "rb") as f:
        sb.storage.from_(bucket).upload(remote_path, f, {"content-type": "application/octet-stream", "x-upsert": "true"})
    # return public URL if bucket is public
    try:
        url = sb.storage.from_(bucket).get_public_url(remote_path)
        return url
    except Exception:
        return remote_path
