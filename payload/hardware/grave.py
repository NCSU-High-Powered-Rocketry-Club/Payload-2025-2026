"""This is Grave, the part of payload that ejects Zombie."""

import time
import platform

# Imports only if running on Raspberry Pi
if platform.system() == 'Linux':
    # Servo Imports
    # Stepper Motor Imports
    import board  # type: ignore # Only imported when real hardware is used # noqa: PLC0415
    from digitalio import DigitalInOut, Direction  # type: ignore # noqa: PLC0415
    from gpiozero import AngularServo, Device, OutputDevice
    from gpiozero.pins.pigpio import PiGPIOFactory

from payload.base_classes.base_grave import BaseGrave
from payload.data_handling.packets.grave_data_packet import GraveDataPacket


class ServoDriver:
    """Driver for the latch servo."""

    # Pin should be 24
    def __init__(
        self, pin=13, min_angle=0, max_angle=198, min_pwm_signal=0.00075, max_pwm_signal=0.00225
    ):
        Device.pin_factory = PiGPIOFactory()

        self.start_angle = max_angle - 1
        self.deploy_angle = max_angle - 40
        self.max_angle = max_angle

        self.servo = AngularServo(
            pin,
            min_angle=min_angle,
            max_angle=max_angle,
            min_pulse_width=min_pwm_signal,
            max_pulse_width=max_pwm_signal,
            initial_angle = self.start_angle,
        )




    def release_latch(self):
        try:
            self.servo.angle = self.start_angle
            time.sleep(0.5)

            self.servo.angle = self.deploy_angle
            time.sleep(0.5)

            self.servo.angle = self.start_angle
            time.sleep(0.5)

        finally:
            print("Released Latch")

    def set_deploy_angle(self, angle):
        if self.servo.min_angle <= angle <= self.servo.max_angle:
            self.deploy_angle = angle
        else:
            raise ValueError(
                f"Angle must be between {self.servo.min_angle} and {self.servo.max_angle}"
            )


class LeadScrewDriver:
    """Driver for the lead screw."""

    def __init__(self, dir_pin=27, step_pin=17, slp_pin=22):

        self.dir = OutputDevice(dir_pin)

        self.step = OutputDevice(step_pin)

        self.slp = OutputDevice(slp_pin, initial_value=False)  # Start in sleep mode — LOW = sleeping on A4988 CHECK THIS WITH GRAVE

    def wake(self):
        self.slp.on()
        time.sleep(0.001)  # A4988 needs ~1ms to wake before stepping

    def sleep(self):
        self.slp.off()

    def move(self, distance_mm, direction="extend"):
        STEPS = int(distance_mm / 0.01)
        microMode = 16
        steps = STEPS * microMode
        if direction == "retract":
            self.dir.on()
        else:
            self.dir.off()

        self.wake()  # Wake before stepping

        for _ in range(steps):
            self.step.on()
            time.sleep(0.00002)
            self.step.off()
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

    __slots__ = ("deployed", "ejecting_zombie", "latch_state", "lead_screw", "servo")

    def __init__(self):
        self.lead_screw = LeadScrewDriver()
        self.deployed = False
        self.latch_state = False
        self.ejecting_zombie = False

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
        self.servo = ServoDriver()
        self.servo.release_latch()
        self.latch_state = True
        time.sleep(5)
        self.ejecting_zombie = True
        self.lead_screw.move(465, direction="deploy")  # mm
        time.sleep(5)
        self.lead_screw.move(120, direction="retract")  # mm

    def get_data_packet(self):
        return GraveDataPacket(ejecting_zombie=self.ejecting_zombie, latch=self.latch_state)
