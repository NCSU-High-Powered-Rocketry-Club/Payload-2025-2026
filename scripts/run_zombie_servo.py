import time
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero.devices import Device

class INJORAServoDriver:
    """
    Controller for the INJORA 35KG Digital Servo (360° Continuous Rotation).
    
    PWM spec: 1000µs (full reverse) / 1500µs (stop) / 2000µs (full forward)
    gpiozero Servo maps: value=-1 → min_pulse, value=0 → mid, value=1 → max_pulse
    """

    def __init__(self, pin=23, min_pwm_signal=0.001, max_pwm_signal=0.002):
        Device.pin_factory = PiGPIOFactory()
        self.servo = Servo(
            pin,
            min_pulse_width=min_pwm_signal,
            max_pulse_width=max_pwm_signal,
        )

    def stop(self):
        """Stop rotation and release torque."""
        self.servo.value = None

    def spin(self, duration, speed=1.0):
        """
        Spin the servo for a given duration at a given speed, then stop.

        :param duration: Seconds to spin (positive float).
        :param speed: Float from -1.0 (full reverse) to 1.0 (full forward).
        """
        if duration <= 0:
            raise ValueError("Duration must be a positive number")
        if not -1.0 <= speed <= 1.0:
            raise ValueError("Speed must be between -1.0 and 1.0")

        try:
            self.servo.value = speed
            time.sleep(duration)
        finally:
            self.stop()

    def spin_forward(self, duration, speed=1.0):
        """Spin forward for a given duration. Speed from 0.0 to 1.0."""
        if speed < 0:
            raise ValueError("Use spin_reverse() for reverse rotation")
        self.spin(duration, speed=abs(speed))

    def spin_reverse(self, duration, speed=1.0):
        """Spin in reverse for a given duration. Speed from 0.0 to 1.0."""
        if speed < 0:
            raise ValueError("Speed must be a positive value (0.0 to 1.0)")
        self.spin(duration, speed=-abs(speed))

try:
    servo = INJORAServoDriver(pin=23)
    print("Spinning forward at full speed for 3 seconds...")
    servo.spin_forward(duration=3, speed=1.0)

    print("Spinning reverse at half speed for 2 seconds...")
    servo.spin_reverse(duration=2, speed=0.5)
except KeyboardInterrupt:
    print("Interrupted by user, stopping servo...")