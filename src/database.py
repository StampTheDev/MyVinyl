from supabase import create_client
from pathlib import Path
from config import SUPABASE_KEY, SUPABASE_URL

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_all_records():
    response = (
        supabase.table("records")
        .select("*")
        .execute()
    )
    return response.data

def get_song_by_nfcid(nfc_id):
    response = (
        supabase.table("records")
        .select("songs(*)")
        .eq("nfc_id", nfc_id)
        .maybe_single()
        .execute()
    )

    if response is None:
        return None

    return response.data["songs"]

def download_song(storage_path):
    audio_data = (
        supabase.storage
        .from_("Local Songs")
        .download(storage_path)
    )

    cache_directory = Path("song_cache")
    cache_directory.mkdir(exist_ok=True)

    local_path = cache_directory / Path(storage_path).name

    with open(local_path, "wb") as file:
        file.write(audio_data)

    return local_path
