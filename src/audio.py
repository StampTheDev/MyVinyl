import subprocess
import threading
import time

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 48000
CHANNELS = 2

volume = 0.2

manual_stop = threading.Event()


def find_audio_device():

    devices = sd.query_devices()

    for index, device in enumerate(devices):

        if (
            "MAX98357A" in device["name"]
            and device["max_output_channels"] >= CHANNELS
        ):
            return index

    raise RuntimeError(
        "Could not find MAX98357A audio device"
    )


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

    audio = audio.reshape(
        -1,
        CHANNELS
    )

    return audio


def play_song(local_path):

    print(f"Decoding {local_path}")
    audio = decode_song(local_path)
    device = find_audio_device()
    output = audio * volume
    print(f"Playing {local_path}")

    manual_stop.clear()

    sd.play(
        output,
        samplerate=SAMPLE_RATE,
        device=device
    )

    stream = sd.get_stream()

    while stream.active:

        if manual_stop.is_set():
            sd.stop()
            return

        time.sleep(0.02)


def stop_song():

    manual_stop.set()
