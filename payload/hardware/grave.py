"""This is Grave, the part of payload that ejects Zombie."""

import time
from payload.data_handling.packets.grave_data_packet import GraveDataPacket
from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import board
from digitalio import DigitalInOut, Direction

class Grave:
    """A mock class representing a graveyard for testing purposes."""

    __slots__ = ("servo_extension_position",)

    def __init__(self):
        """
        Initializes the Grave instance.
        """

    def deploy_zombie(self) -> None:
        """
        The deployment of a zombie payload.
        """
        SERVO_PIN = 18     # GPIO pin connected to servo signal

        # GPIOZero docs recommend using the pigpio daemon to improve
        # PWM precision.
        Device.pin_factory = PiGPIOFactory()

        servo = Servo(SERVO_PIN, initial_value=0)

        print("Servo initialized at center")

        print("Move to LEFT")
        servo.min()
        time.sleep(0.5)

        print("Center")
        servo.mid()
        time.sleep(0.5)

        # call function to release latch, then run lead screw motor.
        DISTANCE = 50 #mm
        STEPS = int(DISTANCE / 0.01)

        DIR = DigitalInOut(board.D27)
        DIR.direction = Direction.OUTPUT
        STEP = DigitalInOut(board.D22)
        STEP.direction = Direction.OUTPUT

        microMode = 16
        # full rotation multiplied by the microstep divider
        steps = STEPS * microMode

        for i in range(steps):
            STEP.value = True
            time.sleep(0.002)
            STEP.value = False
            time.sleep(0.002)
        # 1 second delay before starting again
        time.sleep(1)


    # Ask Jackson: Is this airbreaks code?
    def get_motor_extension(self):
        servo_extension_position = 0
        return servo_extension_position # temporary change as needed

    def get_data_packet(self):
        return GraveDataPacket(position=self.get_motor_extension())