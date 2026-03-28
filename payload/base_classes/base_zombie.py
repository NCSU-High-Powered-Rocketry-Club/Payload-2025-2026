"""Base class for ZOMBIE."""

from abc import ABC, abstractmethod


class BaseZombie(ABC):
    """Class for base zombie code."""

    @abstractmethod
    def start(self) -> None:
        """Starts the zombie for processing data packets."""

    @abstractmethod
    def stop(self) -> None:
        """Stops the zombie for processing data packets."""

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def process_data_packet(self, data_packet):
        pass

    @abstractmethod
    def deploy_legs(self):
        """Deploys the legs of the zombie to stand it up."""

    @abstractmethod
    def start_drilling(self):
        """Starts the drilling mechanism of the zombie."""

    @abstractmethod
    def stop_drilling(self) -> None:
        """
        Stops the drilling mechanism of the zombie.
        """

    @abstractmethod
    def start_soil_sensor(self) -> None:
        """
        Starts the soil sensor of the zombie.
        """

    @abstractmethod
    def check_deployment(self) -> bool:
        """
        Checks if the zombie deployment is complete.

        :return: True if deployment is complete, False otherwise.
        """

    @abstractmethod
    def check_orientation(self) -> bool:
        """
        Checks if the zombie is upright.

        :return: True if the zombie is upright, False otherwise.
        """

    @abstractmethod
    def get_soil_data(self) -> int:
        """Function to get the soil data from the sensor."""
