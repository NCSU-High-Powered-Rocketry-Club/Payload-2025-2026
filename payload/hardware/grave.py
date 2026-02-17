"""This is Grave, the part of payload that ejects Zombie."""

from payload.data_handling.packets.grave_data_packet import GraveDataPacket


class Grave:
    """A mock class representing a graveyard for testing purposes."""

    __slots__ = ("deployed", "lead_screw", "servo")

    """
    High-level controller for the Grave deployment system.
    Contains no direct GPIO imports.
    """

    def __init__(self, servo_driver, lead_screw_driver):
        self.servo = servo_driver
        self.lead_screw = lead_screw_driver
        self.deployed = False

    def start(self):
        pass

    def update(self):
        # For now, auto-deploy once.
        if not self.deployed:
            self.deploy_zombie()
            self.deployed = True

    def stop(self):
        pass

    def deploy_zombie(self):
        self.servo.release_latch()

        self.lead_screw.extend(50)  # mm


    # Ask Jackson: Is this airbreaks code?
    def get_motor_extension(self):
        return 0

    def get_data_packet(self):
        return GraveDataPacket(position=self.get_motor_extension())
