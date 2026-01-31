import time

from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory


SERVO_PIN = 33  # GPIO33

# GPIOZero docs recommend using the pigpio daemon to improve
# PWM precision.
Device.pin_factory = PiGPIOFactory()

# 5-turn servo pulse range (microseconds)
MIN_PULSE = 500     # full CCW
MID_PULSE = 1500    # center
MAX_PULSE = 2500    # full CW

servo = Servo(
    SERVO_PIN,
    initial_value=0,

    # This expects a time in seconds, so we convert to millis and then sec
    min_pulse_width=(MIN_PULSE / 1000.0) / 1000.0,
    max_pulse_width=(MAX_PULSE / 1000.0) / 1000.0,
)

try:
    print("Centering servo")
    servo.mid()
    time.sleep(2)

    print("Moving to min")
    servo.min()
    time.sleep(2)

    print("Moving to max")
    servo.max()
    time.sleep(2)

    print("Sweeping")
    for cur_value in range(-1, 1, 0.01):
        servo.value = cur_value
        time.sleep(0.02)

finally:
    servo.detach()
