import json
import subprocess
import sys
from pathlib import Path

# Exact relative directory of song cache
CACHE_DIR = Path(__file__).resolve().parent.parent / "song_cache"

# Size limit of cache (5 GB)
MAX_CACHE = 5368709120

# Examines cache and clears space if necessary, and downloads song
def download_song(song):

    # Makes cache directory if it doesn't yet exist
    CACHE_DIR.mkdir(exist_ok=True)

    # Template for file names
    output_template = str(CACHE_DIR / f"{song['id']}.%(ext)s")

    # Estimate download size
    download_size = estimate_download_size(song)

    # Frees up space in cache if needed
    free_up_cache(download_size)

    # Downloads audio file using yt_dlp
    try:
        result = subprocess.run(
            [sys.executable,
             "-m", "yt_dlp",
             "--no-playlist",
             "-f", "bestaudio/best",
             "-o", output_template,
             "--print", "after_move:filepath",
             "--no-simulate",
             song["yt_url"]],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as error:
        print(f"Failed to download {song['custom_name']}")
        print(error.stderr)
        return None

    # Fetch file path from command result
    output_lines = result.stdout.strip().splitlines()
    song_path = Path(output_lines[-1])

    # Actual download may be bigger than estimate ; remove files if overflowed cache
    free_up_cache(0)

    return song_path


# Uses yt_dlp to estimate a song's size before download
def estimate_download_size(song):

    try:
        result = subprocess.run(
            [sys.executable,
             "-m", "yt_dlp",
             "--no-playlist",
             "-f", "bestaudio/best",
             "--dump-single-json",
             "--skip-download",
             song["yt_url"]],
            capture_output=True,
            text=True,
            check=True
        )

    # If yt-dlp fails, return the approximate biggest size allowed (25 MB)
    except subprocess.CalledProcessError as error:
        print(f"Failed to retrieve metadata for {song['custom_name']}")
        print(error.stderr)
        return 26214400

    info = json.loads(result.stdout)

    # If yt-dlp knows the exact number of bytes, return it
    file_size = info.get("filesize")
    if file_size is not None:
        return int(file_size)

    # Otherwise, return yt-dlp's estimate
    file_size = info.get("filesize_approx")
    if file_size is not None:
        return int(file_size)

    # If options fail, return approximate largest file allowed (25 MB)
    return 26214400


# Removes least recently used songs in cache until new file can fit
def free_up_cache(estimated_size):

    # Find size of current cache
    total_cache_size = 0
    LRU = []
    for path in CACHE_DIR.iterdir():
        total_cache_size += path.stat().st_size
        if not path.name.endswith(".part"):
            LRU.append(path)

    # If file can already fit, return without deletion
    if total_cache_size + estimated_size <= MAX_CACHE:
        return

    # Otherwise, a file must be deleted ; prioritize least recently used files
    LRU.sort(key=lambda path: path.stat().st_mtime)

    # Keep deleting LRU files until enough space fills up
    for file in LRU:
    
        if total_cache_size + estimated_size <= MAX_CACHE:
            return

        file_size = file.stat().st_size
        file.unlink()
        total_cache_size -= file_size


# Returns the filepath for a song, if it exists
def get_cached_path(song):

    # Creates the cache directory if it doesnt already exist
    CACHE_DIR.mkdir(exist_ok=True)

    # Get song ID and attempt to find it in cache
    song_id = song["id"]
    matches = list(CACHE_DIR.glob(f"{song_id}.*"))

    # Return path to the match, if not currently being downloaded
    for path in matches:
        if not path.name.endswith(".part"):
            return path

    return None
