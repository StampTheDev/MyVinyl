import subprocess
import threading
import time

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 48000
CHANNELS = 2

volume = 0.5

current_audio = None
playhead = 0

manual_stop = threading.Event()
song_finished = threading.Event()

def find_audio_device():

    devices = sd.query_devices()

    for index, device in enumerate(devices):

        if (
            "MAX98357A" in device["name"]
            and device["max_output_channels"] >= CHANNELS
        ):
            return index

    raise RuntimeError("Could not find MAX98357A audio device")


def decode_song(local_path):

    command = [
        "ffmpeg",
        "-v", "error",
        "-nostdin",
        "-i", str(local_path),
        "-f", "f32le",
        "-acodec", "pcm_f32le",
        "-ac", str(CHANNELS),
        "-ar", str(SAMPLE_RATE),
        "pipe:1"
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        check=True
    )

    audio = np.frombuffer(
        result.stdout,
        dtype=np.float32
    )

    audio = audio.reshape(-1, CHANNELS)
    return audio


def audio_callback(outdata, frames, time_info, status):
    global playhead

    outdata.fill(0)

    if manual_stop.is_set() or current_audio is None:
        raise sd.CallbackStop

    end_pos = min(playhead + frames, len(current_audio))
    frames_available = end_pos - playhead

    if frames_available > 0:
        outdata[:frames_available] = current_audio[playhead:end_pos] * volume
        playhead = end_pos

    if playhead >= len(current_audio):
        raise sd.CallbackStop


def on_song_finished():
    song_finished.set()


def play_song(local_path):

    global current_audio
    global playhead

    song_finished.clear()

    print(f"Decoding {local_path}")
    current_audio = decode_song(local_path)

    if manual_stop.is_set():
        manual_stop.clear()
        current_audio = None
        return

    playhead = 0

    device = find_audio_device()
    print(f"Playing {local_path}")

    with sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        device=device,
        callback=audio_callback,
        finished_callback=on_song_finished
    ):
        song_finished.wait()        

    current_audio = None

    manual_stop.clear()


def stop_song():

    manual_stop.set()


def increase_volume():
    global volume
    volume += 0.01
    if volume > 1.00:
        volume = 1.00
    print(f"Volume: {volume:.2f}")


def decrease_volume():
    global volume
    volume -= 0.01
    if volume < 0:
        volume = 0
    print(f"Volume: {volume:.2f}")
