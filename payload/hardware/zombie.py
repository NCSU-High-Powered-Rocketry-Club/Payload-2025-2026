"""This is Zombie, the part of payload that drills and analyzes soil."""

from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket


class Zombie:
    """A class representing a zombie payload."""

    __slots__ = ("soil_data",)

    def __init__(self):
        pass

    def deploy_legs(self) -> None:
        pass

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
