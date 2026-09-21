from gpiozero import Motor

platter_motor = Motor(
    forward=12,
    backward=13,
    pwm=True
)


def start_motor():
    platter_motor.backward(0.1)


def stop_motor():
    platter_motor.stop()
