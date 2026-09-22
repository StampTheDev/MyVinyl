import subprocess
import threading
import time

import numpy as np
import sounddevice as sd

from platter import *

# Each channel plays 48000 values per second
SAMPLE_RATE = 48000
CHANNELS = 2

# Designated starting volume, updates with user volume changes
volume = 0.5

# Current full audio values array
current_audio = None

# Current index within audio values array
playhead = 0

# Flags for manual song endings, audio ceases, and pausing
manual_stop = threading.Event()
song_finished = threading.Event()
paused = threading.Event()

# Used to cumulate seeking and smoothly apply it
seek_timer = None
pending_seek = 0
initiated_seek = 0

# Finds the correct audio device and returns its index if possible
def find_audio_device():

    devices = sd.query_devices()

    for index, device in enumerate(devices):
        if ("MAX98357A" in device["name"] and device["max_output_channels"] >= CHANNELS):
            return index

    raise RuntimeError("Could not find MAX98357A audio device")


# Decodes a song into a format that we can alter and play
def decode_song(local_path):

    # Uses ffmpeg to convert mp3 cached data into raw float32 PCM
    result = subprocess.run(
        ["ffmpeg",
         "-v", "error",
         "-nostdin",
         "-i", str(local_path),
         "-f", "f32le",
         "-acodec", "pcm_f32le",
         "-ac", str(CHANNELS),
         "-ar", str(SAMPLE_RATE),
         "pipe:1"],
        stdout=subprocess.PIPE,
        check=True
    )

    # Uses NumPy to register raw bytes as float values
    audio = np.frombuffer(
        result.stdout,
        dtype=np.float32
    )

    # Splits the floats across the two channels
    audio = audio.reshape(-1, CHANNELS)

    # Since decoding succeded, mark the file as recently used
    local_path.touch()

    # Do not return decoded info if song has since ended
    if manual_stop.is_set():
        manual_stop.clear()
        current_audio = None
        return None

    return audio


# Populates the next segment of frames for the audio player
def audio_callback(outdata, frames, time_info, status):

    global playhead
    global initiated_seek

    # If user has seeked, change the playhead location accordingly
    playhead += initiated_seek * SAMPLE_RATE
    if playhead < 0:
        playhead = 0
    if current_audio is not None and playhead > len(current_audio):
        playhead = len(current_audio)
    initiated_seek = 0

    # Set the frames to silent so that any emptyness is handled correctly
    outdata.fill(0)

    # Handle manual song ends and pauses
    if manual_stop.is_set() or current_audio is None:
        raise sd.CallbackStop
    if paused.is_set():
        return

    # Fill in next frames and adjust playhead
    end_pos = min(playhead + frames, len(current_audio))
    frames_available = end_pos - playhead
    if frames_available > 0:
        outdata[:frames_available] = current_audio[playhead:end_pos] * volume
        playhead = end_pos
    if playhead >= len(current_audio):
        raise sd.CallbackStop


# Helper function for music player that signals audio has ceased
def on_song_finished():
    song_finished.set()


# Plays a song's audio
def play_song(audio):

    global current_audio
    global playhead
    global volume

    song_finished.clear()
    current_audio = audio
    playhead = 0
    volume = 0.5

    # Find audio device and play aloud, wait until song ends
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


# Helper function that signals a manual stop
def end_current_song():
    manual_stop.set()


# Increments the volume by the set increment; keeps volume in range 0-1
def increment_volume(increment):
    global volume
    volume += increment
    if volume > 1.00:
        volume = 1.00
    if volume < 0.00:
        volume = 0


# Applies and cumulated seeking and smoothly adjusts volume
def perform_seek():
    global seek_timer
    global pending_seek
    global initiated_seek

    # Calculate volume rampup info, since it varies by volume and seekage
    seekage = min(10, abs(pending_seek))
    volume_increment = volume / 10

    initiated_seek = pending_seek
    pending_seek = 0
    seek_timer = None

    # Set volume lower, and increment volume back up to make seek smoother
    increment_volume(-1 * seekage * volume_increment)
    for i in range(11 - seekage, 11):
        increment_volume(volume_increment)
        time.sleep(0.05)


# Attempts to seek; seeks done in quick succession are added up
def seek(seconds):
    global seek_timer
    global pending_seek

    pending_seek += seconds

    # Seeks are applied only if seek timer goes off when no seeks occur in 0.1 seconds
    if seek_timer is not None:
        seek_timer.cancel()
    seek_timer = threading.Timer(0.1, perform_seek)
    seek_timer.start()


# Signals the current song to stop and controls motor accordingly
def toggle_pause():
    if paused.is_set():
        paused.clear()
        start_motor()
    else:
        paused.set()
        stop_motor()
