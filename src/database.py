from supabase import create_client
from config import SUPABASE_KEY, SUPABASE_URL

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def retrieve_playlist(nfc_id):

    response = (
        supabase
        .table("songs")
        .select("id", "yt_url, name")
        .eq("record_id", nfc_id)
        .order("playlist_order")
        .execute()
    )

    return response.data
