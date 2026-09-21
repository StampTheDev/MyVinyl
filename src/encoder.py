import threading

from gpiozero import RotaryEncoder, Button
from audio import *
from player import *

# Used to identify paused state and detect dual-button combo
pause_timer = None
paused = False

# Detects when go_back and skip buttons were recently pushed
go_back_detect = False
skip_detect = False

# Decreases the volume by 0.01, disabled if paused
def volume_down():
    if not paused:
        increment_volume(-0.01)


# Increases the volume by 0.01, disabled if paused
def volume_up():
    if not paused:
        increment_volume(0.01)


# Seeks backward by one second, disabled if paused
def seek_back():
    if not paused:
        seek(-1)


# Seeks forward by one second, disabled if paused
def seek_forward():
    if not paused:
        seek(1)


# Sends "go back" signal to button mapper
def attempt_go_back():
    button_mapper("go_back")


# Sends "skip" signal to button mapper
def attempt_skip():
    button_mapper("skip")


# Identifies action after a brief window following a button press
def button_control():
    
    global pause_timer
    global paused
    global go_back_detect
    global skip_detect

    # If both buttons pushed, toggle a pause
    if go_back_detect and skip_detect:
        toggle_pause()
        if paused:
            paused = False
        else:
            paused = True

    # If only one button, attempt to perform that action
    elif go_back_detect:
        if not paused:
            go_back()
    else:
        if not paused:
            skip()

    pause_timer = None
    go_back_detect = False
    skip_detect = False


# Maps button presses to signals, and calculates action after a short window
def button_mapper(cmd):
    global pause_timer
    global go_back_detect
    global skip_detect

    # After the first button press, signals are identified after 0.1 seconds
    if pause_timer is None:
        pause_timer = threading.Timer(0.1, button_control)
        pause_timer.start()

    # Raise detection flags based on command
    if cmd == "go_back":
        go_back_detect = True
    if cmd == "skip":
        skip_detect = True


# Volume Knob / Go Back Button
# Rotate CCW to reduce volume, CW to increase volume
# Press knob in to go back a song
volume_encoder = RotaryEncoder(17, 27, max_steps=0)
volume_encoder.when_rotated_counter_clockwise = volume_down
volume_encoder.when_rotated_clockwise = volume_up

go_back_button = Button(22, bounce_time=0.1)
go_back_button.when_pressed = attempt_go_back

# Seek Knob / Skip Button
# Rotate CCW to seek backward, CW to seek forward
# Press knob in to skip sonh
seek_encoder = RotaryEncoder(23, 24, max_steps=0)
seek_encoder.when_rotated_counter_clockwise = seek_back
seek_encoder.when_rotated_clockwise = seek_forward

skip_button = Button(25, bounce_time=0.1)
skip_button.when_pressed = attempt_skip

# Press both knobs in at the same time to pause/unpause
