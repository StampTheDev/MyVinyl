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

seek_timer = None
pending_seek = 0
initiated_seek = 0
seek_steps = 0

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

    if manual_stop.is_set():
        manual_stop.clear()
        current_audio = None
        return None

    return audio


def audio_callback(outdata, frames, time_info, status):

    global playhead
    global initiated_seek
    playhead += initiated_seek
    if playhead < 0:
        playhead = 0
    if playhead > len(current_audio):
        playhead = len(current_audio)
    initiated_seek = 0

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


def on_song_start():
    song_finished.clear()


def play_song(audio):

    global current_audio
    global playhead

    song_finished.clear()

    current_audio = audio
    playhead = 0

    device = find_audio_device()

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


def end_current_song():

    manual_stop.set()


def increment_volume(increment):
    global volume
    volume += increment
    if volume > 1.00:
        volume = 1.00
    if volume < 0.00:
        volume = 0
    print(f"Volume: {volume:.2f}")


def perform_seek():
    global seek_timer
    global pending_seek
    global initiated_seek
    global seek_steps

    prev_steps = min(10, seek_steps)
    seek_steps = 0
    initiated_seek = pending_seek
    pending_seek = 0
    seek_timer = None
    volume_increment = volume / 10
    increment_volume(-1 * prev_steps * volume_increment)
    for i in range(11 - prev_steps, 11):
        increment_volume(volume_increment)
        time.sleep(0.05)


def seek(seconds):
    global seek_timer
    global pending_seek
    global seek_steps

    pending_seek += SAMPLE_RATE * seconds

    if seek_timer is not None:
        seek_timer.cancel()
    seek_steps += 1
    seek_timer = threading.Timer(0.1, perform_seek)
    seek_timer.start()
