from gpiozero import RotaryEncoder, Button
from audio import *

def volume_down():
    increment_volume(-0.01)

def volume_up():
    increment_volume(0.01)

def seek_back():
    seek(-1)

def seek_forward():
    seek(1)
    
volume_encoder = RotaryEncoder(17, 27, max_steps=0)
volume_encoder.when_rotated_counter_clockwise = volume_down
volume_encoder.when_rotated_clockwise = volume_up

#restart_button = Button(22, bounce_time=0.1)
#restart_button.when_pressed = end_song

seek_encoder = RotaryEncoder(23, 24, max_steps=0)
seek_encoder.when_rotated_counter_clockwise = seek_back
seek_encoder.when_rotated_clockwise = seek_forward

#pause_button = Button(25, bounce_time=0.1)
#pause_button.when_pressed = pause_song
