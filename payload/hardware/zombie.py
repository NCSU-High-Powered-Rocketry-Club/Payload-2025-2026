"""This is Zombie, the part of payload that drills and analyzes soil."""

import asyncio
import threading

from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

from payload import constants
from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket

# GPIOZero docs recommend using the pigpio daemon to improve
# PWM precision.
Device.pin_factory = PiGPIOFactory()


class Zombie:
    """A class representing a zombie payload."""

    __slots__ = (
        "_lift",
        "_motor",
        "drilling_complete",
        "legs_deployed",
        "soil_data",
    )

    def __init__(self):
        # A flag to mark when the legs have been successfully deployed
        self.legs_deployed = False

        # A flag to mark when drilling is completed
        self.drilling_complete = False

        # Define our motor and lift objects. Since both communicate over standard
        # RC PWM, we use gpiozero.Servo objects to represent them.
        self._motor = Servo(
            constants.DRILL_MOTOR_PIN,
            initial_value=0,
        )

        self._lift = Servo(
            constants.LIFT_SERVO_PIN,
            initial_value=constants.LIFT_UP_POSITION,
            # This expects a time in seconds, so we convert to millis and then sec
            min_pulse_width=(constants.LIFT_SERVO_MIN_PULSE / 1000.0) / 1000.0,
            max_pulse_width=(constants.LIFT_SERVO_MAX_PULSE / 1000.0) / 1000.0,
        )

    def deploy_legs(self) -> None:
        """
        Deploy the legs.
        """
        self.legs_deployed = True

    def start_drill_sequence(self) -> None:
        """
        Start the drilling sequence in a thread, so we can run the sequence asynchronously.
        """
        self.drill_thread = threading.Thread(
            target=asyncio.run, args=(self.run_drilling_sequence(),), daemon=True
        )
        self.drill_thread.start()

    async def run_drilling_sequence(self) -> None:
        """
        Starts the drilling mechanism of the zombie.
        """
        # We assume our lift is in the topmost position.
        # TODO: Have a procedure in the checklist to verify that the servo is
        # in that position.

        # Start the drill off.
        self._motor.value = 0
        print("About to start drilling...")

        # Initial wait
        await asyncio.sleep(constants.DRILL_START_DELAY)

        print("Starting drilling sequence.")

        # Start spinning the drill
        self._motor.value = constants.DRILL_SPEED * constants.DRILL_SPIN_DIR

        await asyncio.sleep(constants.LIFT_START_DELAY)

        self._lift.value = constants.LIFT_DOWN_POSITION

        print("Drilling...")
        await asyncio.sleep(constants.DRILL_TIME)

        print("Retracting...")
        self._lift.value = constants.LIFT_UP_POSITION

        await asyncio.sleep(constants.RETRACTION_TIME)

        # Stop the drill.
        self._motor.value = 0
        print("Drilling complete. Pick up your dirt on the way out.")

        self.drilling_complete = True

    def start_soil_sensor(self) -> None:
        """
        Starts the soil sensor of the zombie.
        """

    def get_soil_data(self):
        """ """
        soil_data = 0
        return soil_data  # temporary change as needed

    def get_data_packet(self):
        """ """
        return ZombieDataPacket(soil_info=self.get_soil_data())
