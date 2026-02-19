"""This is Grave, the part of payload that ejects Zombie."""

import time

# Lead screw imports
import board
from digitalio import DigitalInOut, Direction

# Servo imports
from gpiozero import AngularServo, Device
from gpiozero.pins.pigpio import PiGPIOFactory

from payload.data_handling.packets.grave_data_packet import GraveDataPacket


class ServoDriver:
    """Driver for the latch servo."""

    def __init__(self, pin=24, min_angle=0, max_angle=198, min_pwm_signal=0.00075, max_pwm_signal=0.00225):
        Device.pin_factory = PiGPIOFactory()

        self.servo = AngularServo(pin, min_angle=min_angle, max_angle=max_angle, min_pulse_width=min_pwm_signal, max_pulse_width=max_pwm_signal)

        self.start_angle = max_angle
        self.deploy_angle = max_angle - 15
        self.max_angle = max_angle

    def release_latch(self):
        try:
            self.servo.angle = self.start_angle
            time.sleep(0.5)

            self.servo.angle = self.deploy_angle
            time.sleep(0.5)

            self.servo.angle = self.start_angle
            time.sleep(0.5)

        finally:
            self.servo.angle = None  # Release torque

    def set_deploy_angle(self, angle):
        if self.servo.min_angle <= angle <= self.servo.max_angle:
            self.deploy_angle = angle
        else:
            raise ValueError(
                f"Angle must be between {self.servo.min_angle} and {self.servo.max_angle}"
            )


class LeadScrewDriver:
    """Driver for the lead screw."""

    def __init__(self, dir_pin=board.D27, step_pin=board.D22):
        self.dir = DigitalInOut(dir_pin)
        self.dir.direction = Direction.OUTPUT

        self.step = DigitalInOut(step_pin)
        self.step.direction = Direction.OUTPUT

    def extend(self, distance_mm):
        STEPS = int(distance_mm / 0.01)
        microMode = 16
        steps = STEPS * microMode

        self.dir.value = False  # Set direction to extend

        for _ in range(steps):
            self.step.value = True
            time.sleep(0.0005)
            self.step.value = False
            time.sleep(0.0005)

        time.sleep(1)


# =========================
# Grave High-Level Controller
# =========================


class Grave:
    """
    High-level controller for the Grave deployment system.
    """

    __slots__ = ("deployed", "lead_screw", "servo")

    def __init__(self):
        self.servo = ServoDriver()
        self.lead_screw = LeadScrewDriver()
        self.deployed = False

    def start(self):
        pass

    def update(self):
        if not self.deployed:
            self.deploy_zombie()
            self.deployed = True

    def stop(self):
        pass

    def deploy_zombie(self):
        self.servo.release_latch()
        self.lead_screw.extend(50)  # mm

    def get_motor_extension(self):
        return 0

    def get_data_packet(self):
        return GraveDataPacket(position=self.get_motor_extension())
