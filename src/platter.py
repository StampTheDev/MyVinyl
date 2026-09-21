from gpiozero import Motor

# Initialize generic motor object
platter_motor = Motor(
    forward=12,
    backward=13,
    pwm=True
)

# Starts the motor at normal speed, clockwise
def start_motor():
    platter_motor.forward(0.12)


# Stops the motor
def stop_motor():
    platter_motor.stop()
