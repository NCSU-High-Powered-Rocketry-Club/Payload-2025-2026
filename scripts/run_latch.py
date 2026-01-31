import time

from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# --------------------
# GPIO SETUP
# --------------------
SERVO_PIN = 18     # GPIO pin connected to servo signal

# GPIOZero docs recommend using the pigpio daemon to improve
# PWM precision.
Device.pin_factory = PiGPIOFactory()

servo = Servo(SERVO_PIN, initial_value=0)

print("Servo initialized at center")

try:
    while True:
        print("Move to LEFT")
        servo.min()
        time.sleep(2)

        print("Center")
        servo.mid()
        time.sleep(2)

        print("Move to RIGHT")
        servo.max()
        time.sleep(2)

        print("Center")
        servo.mid()
        time.sleep(2)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    servo.detach()
    print("GPIO cleaned up")
    