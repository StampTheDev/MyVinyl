import subprocess
from pathlib import Path
import socket
import json
import time
import threading

mpv_process = None
mpv_connection = None
MPV_SOCKET = "/tmp/myvinyl-mpv.socket"

song_finished = threading.Event()
send_lock = threading.Lock()

def connect_to_mpv():
    global mpv_connection

    for _ in range(50):
        try:
            connection = socket.socket(
                socket.AF_UNIX,
                socket.SOCK_STREAM
            )

            connection.connect(MPV_SOCKET)

            mpv_connection = connection
            return

        except (ConnectionRefusedError, FileNotFoundError):
            time.sleep(0.1)

    raise RuntimeError("Could not connect to MPV")


def listen_for_mpv_events():

    response_file = mpv_connection.makefile("r")

    for line in response_file:
        message = json.loads(line)

        if message.get("event") == "end-file" and message.get("reason") in ("eof", "stop"):
            song_finished.set()


def wait_for_mpv():
    for _ in range(50):
        if mpv_process.poll() is not None:
            raise RuntimeError("MPV exited while starting.")

        if Path(MPV_SOCKET).exists():
            return

        time.sleep(0.1)

    raise RuntimeError("MPV failed to become ready.")

def start_mpv():
    global mpv_process

    socket_path = Path(MPV_SOCKET)
    if socket_path.exists():
        socket_path.unlink()

    mpv_process = subprocess.Popen([
        "mpv",
        "--idle=yes",
        "--no-video",
        "--no-config",
        "--terminal=no",
        "--keep-open=yes",
        "--audio-stream-silence=yes",
        "--audio-device=alsa/plughw:CARD=MAX98357A,DEV=0",
        "--volume=40",
        f"--input-ipc-server={MPV_SOCKET}"
    ])

    connect_to_mpv()

    listener = threading.Thread(
        target=listen_for_mpv_events,
        daemon=True
    )

    listener.start()

    print("Listener enabled")


def stop_mpv():
    global mpv_process
    global mpv_connection

    if mpv_process is None:
        return

    try:
        send_command(["quit"])
        mpv_process.wait(timeout=2)

    except Exception:
        if mpv_process.poll() is None:
            mpv_process.terminate()

        mpv_process.wait()

    finally:
        if mpv_connection is not None:
            mpv_connection.close()
            mpv_connection = None

        mpv_process = None


def send_command(command):
    message = json.dumps({
        "command": command
    })

    with send_lock:
        mpv_connection.sendall((message + "\n").encode())


def play_song(local_path):
    full_path = str(Path(local_path).resolve())
    song_finished.clear()
    send_command(["loadfile", full_path, "replace"])



