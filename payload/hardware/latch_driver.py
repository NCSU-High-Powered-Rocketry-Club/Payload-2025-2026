import time
from gpiozero import Device, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

class ServoDriver:
    def __init__(self, pin=24, min_angle=0, max_angle=198, min_pulse_width = 0.00075, max_pulse_width = 0.00225):
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
        self.servo = AngularServo(pin, min_angle=min_angle, max_angle=max_angle,min_pulse_width = min_pulse_width, max_pulse_width = max_pulse_width)

        # Store deployment angles for convenience
        self.start_angle = 190
        self.deploy_angle = 160
        self.max_angle = max_angle

    def release_latch(self):
        """
        Moves the servo to deploy the latch safely, then stops PWM.
        """
        try:
            print("Servo initialized. Moving to starting position...")
            self.servo.angle = self.start_angle
            time.sleep(2)
            print("Deploying latch...")
            self.servo.angle = self.deploy_angle
            time.sleep(2)

            print("Returning to start position...")
            self.servo.angle = self.start_angle
            time.sleep(2)

        finally:
            # Stop sending PWM to release torque
            self.servo.angle = None
            print("Servo released.")

    def set_deploy_angle(self, angle):
        """
        Allows overriding the default deployment angle if needed.
        """
        if self.servo.min_angle <= angle <= self.servo.max_angle:
            self.deploy_angle = angle
        else:
            raise ValueError(f"Angle must be between {self.servo.min_angle} and {self.servo.max_angle}")
