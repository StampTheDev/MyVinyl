import subprocess

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 48000
CHANNELS = 2

volume = 0.05


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

    sd.play(
        output,
        samplerate=SAMPLE_RATE,
        device=device
    )

    sd.wait()


def stop_song():

    sd.stop()
