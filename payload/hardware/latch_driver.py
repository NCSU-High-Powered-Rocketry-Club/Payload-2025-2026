"""General file for the latch servo driver."""

import time

from gpiozero import AngularServo, Device
from gpiozero.pins.pigpio import PiGPIOFactory


class ServoDriver:
    """Driver for the latch servo."""

    def __init__(self, pin=24, min_angle=0, max_angle=30):
        """
        Initializes the ServoDriver for a non-continuous servo.

        Args:
            pin (int): GPIO pin the servo is connected to.
            min_angle (float): Minimum angle of the servo (fully retracted).
            max_angle (float): Maximum angle of the servo (fully extended).
        """
        # Use PiGPIOFactory for accurate PWM timing
        Device.pin_factory = PiGPIOFactory()

        # Create AngularServo for non-continuous servo
        self.servo = AngularServo(pin, min_angle=min_angle, max_angle=max_angle)

        # Store deployment angles for convenience
        self.start_angle = min_angle
        self.deploy_angle = (min_angle + max_angle) / 2  # default middle
        self.max_angle = max_angle

    def release_latch(self):
        """
        Moves the servo to deploy the latch safely, then stops PWM.
        """
        try:
            self.servo.angle = self.start_angle
            time.sleep(0.5)

            self.servo.angle = self.deploy_angle
            time.sleep(0.5)

            self.servo.angle = self.start_angle
            time.sleep(0.5)

        finally:
            # Stop sending PWM to release torque
            self.servo.angle = None

    def set_deploy_angle(self, angle):
        """
        Allows overriding the default deployment angle if needed.
        """
        if self.servo.min_angle <= angle <= self.servo.max_angle:
            self.deploy_angle = angle
        else:
            raise ValueError(
                f"Angle must be between {self.servo.min_angle} and {self.servo.max_angle}"
            )
