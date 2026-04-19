"""A mock implementation of the Zombie class for testing purposes."""

from payload.base_classes.base_zombie import BaseZombie
from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket


class MockZombie(BaseZombie):
    """A mock implementation of the Zombie class for testing purposes."""

    __slots__ = ("activating_legs", "checking_orientation", "soil_data")

    def __init__(self):
        self.soil_data = 0
        self.activating_legs = False
        self.checking_orientation = False

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def update(self):
        pass

    def process_data_packet(self, data_packet):
        pass

    def deploy_legs(self) -> None:
        self.activating_legs = True
        pass

    def start_drilling(self) -> None:
        pass

    def stop_drilling(self) -> None:
        pass

    def start_soil_sensor(self) -> None:
        pass

    def check_deployment(self) -> bool:
        return True

    def check_orientation(self) -> bool:
        self.checking_orientation = True
        return True

    def get_soil_data(self):
        """Function to get the soil data from the sensor."""
        return self.soil_data

    def get_data_packet(self):
        """Get the data packet for zombie. This will involve firm data and soil sensor data."""
        return ZombieDataPacket(soil_info=self.get_soil_data(), activating_legs=self.activating_legs, checking_orientation=self.checking_orientation)
