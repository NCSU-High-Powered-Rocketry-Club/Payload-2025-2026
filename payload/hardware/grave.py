"""This is Grave, the part of payload that ejects Zombie."""

from payload.data_handling.packets.grave_data_packet import GraveDataPacket

class Grave:
    """A mock class representing a graveyard for testing purposes."""

    __slots__ = ("servo_extension_position",)

    def __init__(self):
        """
        Initializes the Grave instance.
        """

    def deploy_zombie(self) -> None:
        """
        The deployment of a zombie payload.
        """
        # call function to release latch, then run lead screw motor.

    # Ask Jackson: Is this airbreaks code?
    def get_motor_extension(self):
        servo_extension_position = 0
        return servo_extension_position # temporary change as needed

    def get_data_packet(self):
        return GraveDataPacket(position=self.get_motor_extension())