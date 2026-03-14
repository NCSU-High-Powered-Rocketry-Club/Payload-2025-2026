"""This is Zombie, the part of payload that drills and analyzes soil."""

import time

from gpiozero import Servo
from gpiozero.devices import Device
from gpiozero.pins.pigpio import PiGPIOFactory

from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket


class Zombie:
    """A class representing a zombie payload."""

    __slots__ = ("soil_data",)

    def __init__(self):
        pass

    def deploy_legs(self) -> None:
        """
        Deploys the legs of the zombie to stand it up.
        """
        try:
            servo = INJORAServoDriver(pin=16)
            servo.spin_forward(duration=10, speed=1.0)
        finally:
            servo.stop()

    def start_drilling(self) -> None:
        """
        Starts the drilling mechanism of the zombie.
        """

    def stop_drilling(self) -> None:
        """
        Stops the drilling mechanism of the zombie.
        """

    def start_soil_sensor(self) -> None:
        """
        Starts the soil sensor of the zombie.
        """

    def check_deployment(self) -> bool:
        """
        Checks if the zombie deployment is complete.

        :return: True if deployment is complete, False otherwise.
        """

    def check_orientation(self) -> bool:
        """
        Checks if the zombie is upright.

        :return: True if the zombie is upright, False otherwise.
        """

    def get_soil_data(self):
        """Function to get the soil data from the sensor."""
        return 0

    def get_data_packet(self):
        """Get the data packet for zombie. This will involve firm data and soil sensor data."""
        return ZombieDataPacket(soil_info=self.get_soil_data())


class INJORAServoDriver:
    """
    Controller for the INJORA 35KG Digital Servo (360° Continuous Rotation).

    PWM spec: 1000µs (full reverse) / 1500µs (stop) / 2000µs (full forward)
    gpiozero Servo maps: value=-1 → min_pulse, value=0 → mid, value=1 → max_pulse
    """

    def __init__(self, pin=16, min_pwm_signal=0.001, max_pwm_signal=0.002):
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
