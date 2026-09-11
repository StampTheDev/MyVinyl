import subprocess
from pathlib import Path


def play_song(local_path):
    path = Path(local_path)

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    subprocess.run([
        "mpv",
        "--audio-device=alsa/plughw:CARD=MAX98357A,DEV=0",
        "--no-video",
        "--no-config",
        "--volume=20",
        str(path)
    ])
