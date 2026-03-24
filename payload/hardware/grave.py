"""This is Grave, the part of payload that ejects Zombie."""

import time

# Servo imports
from gpiozero import AngularServo, Device
from gpiozero.pins.pigpio import PiGPIOFactory

from payload.base_classes.base_grave import BaseGrave
from payload.data_handling.packets.grave_data_packet import GraveDataPacket


class ServoDriver:
    """Driver for the latch servo."""

    # Pin should be 24
    def __init__(
        self, pin=24, min_angle=0, max_angle=198, min_pwm_signal=0.00075, max_pwm_signal=0.00225
    ):
        Device.pin_factory = PiGPIOFactory()

        self.servo = AngularServo(
            pin,
            min_angle=min_angle,
            max_angle=max_angle,
            min_pulse_width=min_pwm_signal,
            max_pulse_width=max_pwm_signal,
        )

        self.start_angle = max_angle - 1
        self.deploy_angle = max_angle - 40
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

    def __init__(self, dir_pin=None, step_pin=None, slp_pin=None):
        import board  # type: ignore # Only imported when real hardware is used # noqa: PLC0415
        from digitalio import DigitalInOut, Direction  # type: ignore # noqa: PLC0415

        dir_pin = dir_pin or board.D27
        step_pin = step_pin or board.D22
        slp_pin = slp_pin or board.D17

        self.dir = DigitalInOut(dir_pin)
        self.dir.direction = Direction.OUTPUT

        self.step = DigitalInOut(step_pin)
        self.step.direction = Direction.OUTPUT

        self.slp = DigitalInOut(slp_pin)
        self.slp.direction = Direction.OUTPUT
        self.slp.value = False  # Start in sleep mode — LOW = sleeping on A4988

    def wake(self):
        self.slp.value = True
        time.sleep(0.001)  # A4988 needs ~1ms to wake before stepping

    def sleep(self):
        self.slp.value = False

    def move(self, distance_mm, direction="extend"):
        STEPS = int(distance_mm / 0.01)
        microMode = 16
        steps = STEPS * microMode
        self.dir.value = direction == "retract"

        self.wake()  # Wake before stepping

        for _ in range(steps):
            self.step.value = True
            time.sleep(0.00002)
            self.step.value = False
            time.sleep(0.00002)

        time.sleep(1)
        self.sleep()  # Return to sleep after move completes


# =========================
# Grave High-Level Controller
# =========================


class Grave(BaseGrave):
    """
    High-level controller for the Grave deployment system.
    """

    __slots__ = ("deployed", "latch_state", "lead_screw", "motor_extention", "servo")

    def __init__(self):
        self.servo = ServoDriver()
        self.lead_screw = LeadScrewDriver()
        self.deployed = False
        self.latch_state = 0
        self.motor_extention = 0

    # TODO: use these when giving grave its own thread
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
        self.latch_state = 1
        time.sleep(2)
        self.motor_extention = 1
        self.lead_screw.move(470, direction="extend")  # mm
        time.sleep(5)
        self.lead_screw.move(80, direction="retract")  # mm

    def get_data_packet(self):
        return GraveDataPacket(position=self.motor_extention, latch=self.latch_state)
