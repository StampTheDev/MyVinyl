import subprocess
import sys
from pathlib import Path

# Exact relative directory of song cache
CACHE_DIR = Path(__file__).resolve().parent.parent / "song_cache"

# Downloads a song and returns the path to the file in cache
def download_song(song):

    # Makes cache directory if it doesn't yet exist
    CACHE_DIR.mkdir(exist_ok=True)

    # Template for file names
    output_template = str(
        CACHE_DIR / f"{song['id']}.%(ext)s"
    )

    # Downloads audio file using yt_dlp
    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--no-playlist",
        "-f",
        "bestaudio/best",
        "-o",
        output_template,
        "--print",
        "after_move:filepath",
        "--no-simulate",
        song["yt_url"]
    ]

    try:
        result = subprocess.run(
            command,
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
    return song_path

# Returns the filepath for a song, if it exists
def get_cached_path(song):

    song_id = song["id"]

    matches = list(
        CACHE_DIR.glob(f"{song_id}.*")
    )

    for path in matches:
        if not path.name.endswith(".part"):
            return path

    return None
