import time

from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# --------------------
# GPIO SETUP
# --------------------
PWM_PIN = 32  # PWM0

# GPIOZero docs recommend using the pigpio daemon to improve
# PWM precision.
Device.pin_factory = PiGPIOFactory()

motor = Servo(
    PWM_PIN,
    initial_value=0,
    min_pulse_width=1 / 1000,
    max_pulse_width=2 / 1000,
)

def ramp(motor: Servo, start, end, step=0.05, delay=0.05):
    """Helper to test motor ramping"""

    if start < end:
        value_range = [x * step for x in range(int(start / step), int(end / step) + 1)]
    else:
        value_range = [x * step for x in range(int(start / step), int(end / step) - 1, -1)]

    for dc in value_range:
        motor.value = dc
        time.sleep(delay)


print("Motor initialized. Testing discrete values.")

try:
    # FORWARD
    print("Forward (100%)")
    motor.value = 1  # Adjust as needed
    time.sleep(3)

    # STOP
    print("Stop")
    motor.value = 0
    time.sleep(2)

    # REVERSE
    print("Reverse (100%)")
    motor.value = -1
    time.sleep(3)

    # STOP
    print("Stop")
    motor.value = 0
    time.sleep(2)

    # smooth forward
    print("Ramp up (0 - 100)")
    ramp(motor, 0, 1)
    time.sleep(2)

    # smooth stop
    print("Ramp down (100 - 0)")
    ramp(motor, 1, 0)

except KeyboardInterrupt:
    print("Interrupted")

finally:
    motor.detach()
    print("GPIO cleaned up")
