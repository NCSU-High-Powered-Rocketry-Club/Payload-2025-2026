import time
from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory


class ServoDriver:
    def __init__(self, pin=24):
        Device.pin_factory = PiGPIOFactory()
        self.servo = Servo(pin, initial_value=0)

    def release_latch(self):
        print("Servo initialized at center")

        print("Move to LEFT")
        self.servo.min()
        time.sleep(0.1)

        print("Center")
        self.servo.mid()
        time.sleep(0.1)
