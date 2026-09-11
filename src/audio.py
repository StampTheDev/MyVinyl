import subprocess
from pathlib import Path


def play_song(local_path):
    path = Path(local_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    subprocess.run([
        "mpv",
        "--no-video",
        "--no-config",
        "--volume=1",
        str(path)
    ])