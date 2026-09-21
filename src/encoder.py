import threading

from gpiozero import RotaryEncoder, Button
from audio import *
from player import *

pause_timer = None
paused = False
go_back_detect = False
skip_detect = False

def volume_down():
    if not paused:
        increment_volume(-0.01)

def volume_up():
    if not paused:
        increment_volume(0.01)

def seek_back():
    if not paused:
        seek(-1)

def seek_forward():
    if not paused:
        seek(1)

def attempt_go_back():
    coalesce_buttons("go_back")

def attempt_skip():
    coalesce_buttons("skip")

def button_control():
    
    global pause_timer
    global paused
    global go_back_detect
    global skip_detect

    if go_back_detect and skip_detect:
        toggle_pause()
        if paused:
            paused = False
        else:
            paused = True
    elif go_back_detect:
        if not paused:
            go_back()
    else:
        if not paused:
            skip()

    pause_timer = None
    go_back_detect = False
    skip_detect = False


def coalesce_buttons(cmd):
    global pause_timer
    global go_back_detect
    global skip_detect

    if pause_timer is None:
        pause_timer = threading.Timer(0.1, button_control)
        pause_timer.start()
    if cmd == "go_back":
        go_back_detect = True
    if cmd == "skip":
        skip_detect = True

    
volume_encoder = RotaryEncoder(17, 27, max_steps=0)
volume_encoder.when_rotated_counter_clockwise = volume_down
volume_encoder.when_rotated_clockwise = volume_up

go_back_button = Button(22, bounce_time=0.1)
go_back_button.when_pressed = attempt_go_back

seek_encoder = RotaryEncoder(23, 24, max_steps=0)
seek_encoder.when_rotated_counter_clockwise = seek_back
seek_encoder.when_rotated_clockwise = seek_forward

skip_button = Button(25, bounce_time=0.1)
skip_button.when_pressed = attempt_skip
