class Zombie:
    """A class representing a zombie payload."""

    __slots__ = ""

    def __init__(self):
        pass

    def deploy_legs(self) -> None:
        pass

    def start_drilling(self) -> None:
        """
        Starts the drilling mechanism of the zombie.
        """
        pass

    def stop_drilling(self) -> None:
        """
        Stops the drilling mechanism of the zombie.
        """
        pass

    def start_soil_sensor(self) -> None:
        """
        Starts the soil sensor of the zombie.
        """
        pass

    def check_deployment(self) -> bool:
        """
        Checks if the zombie deployment is complete.

        :return: True if deployment is complete, False otherwise.
        """
        pass

    def check_orientation(self) -> bool:
        """
        Checks if the zombie is upright.

        :return: True if the zombie is upright, False otherwise.
        """
        pass
