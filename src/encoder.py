from gpiozero import RotaryEncoder, Button
import time
from audio import *
import subprocess

current_volume = 40
pending_seek = 0
seek_timer = None
seek_steps = 0

def decrease_volume():
    set_volume(current_volume - 1)

def increase_volume():
    set_volume(current_volume + 1)

def restart_song():
    send_command(["seek", 0, "absolute"])

def rewind():
    play_encoder_click()
    add_seek(-0.5)

def fast_forward():
    play_encoder_click()
    add_seek(0.5)

def perform_seek():
    global pending_seek
    global seek_timer
    global seek_steps

    send_command(["seek", pending_seek, "relative+exact"])
    print(f"Seeking: {pending_seek:+.1f}s")

    pending_seek = 0
    seek_timer = None
    prev_steps = min(10, seek_steps)
    seek_steps = 0

    volume_increment = current_volume / 10
    for i in range(11 - prev_steps, 11):
        set_volume(i * volume_increment)
        time.sleep(0.05)


def add_seek(amount):
    global pending_seek
    global seek_timer
    global seek_steps

    pending_seek += amount * (1.1 ** seek_steps)

    if seek_timer is not None:
        seek_timer.cancel()
        seek_steps += 1

    seek_timer = threading.Timer(0.1, perform_seek)
    seek_timer.start()


def pause_song():
    send_command(["cycle", "pause"])

def end_song():
    send_command(["stop"])

def set_volume(level):
    global current_volume

    current_volume = level

    if current_volume > 100:
        current_volume = 100

    if current_volume < 0:
        current_volume = 0

    send_command([
        "set_property",
        "volume",
        current_volume
    ])

    print(f"Volume: {current_volume}%")

def play_encoder_click():
    subprocess.Popen([
        "aplay",
        "-q",
        "-D",
        "plughw:CARD=MAX98357A,DEV=0",
        "/tmp/encoder_click.wav"
    ])
    
volume_encoder = RotaryEncoder(17, 27, max_steps=0)
volume_encoder.when_rotated_counter_clockwise = decrease_volume
volume_encoder.when_rotated_clockwise = increase_volume

restart_button = Button(22, bounce_time=0.1)
restart_button.when_pressed = end_song

seek_encoder = RotaryEncoder(23, 24, max_steps=0)
seek_encoder.when_rotated_counter_clockwise = rewind
seek_encoder.when_rotated_clockwise = fast_forward

pause_button = Button(25, bounce_time=0.1)
pause_button.when_pressed = pause_song
