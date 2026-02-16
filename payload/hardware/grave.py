"""This is Grave, the part of payload that ejects Zombie."""

import time
from payload.data_handling.packets.grave_data_packet import GraveDataPacket


class Grave:
    """A mock class representing a graveyard for testing purposes."""

    __slots__ = ("servo", "lead_screw", "deployed")

    """
    High-level controller for the Grave deployment system.
    Contains no direct GPIO imports.
    """

    def __init__(self, servo_driver, lead_screw_driver):
        self.servo = servo_driver
        self.lead_screw = lead_screw_driver
        self.deployed = False

    def start(self):
        print("Grave system initialized.")

    def update(self):
        # For now, auto-deploy once.
        if not self.deployed:
            self.deploy_zombie()
            self.deployed = True

    def stop(self):
        print("Grave system shutting down.")

    def deploy_zombie(self):
        print("Releasing latch...")
        self.servo.release_latch()

        print("Extending lead screw...")
        self.lead_screw.extend(50)  # mm

        print("Deployment complete.")


    # Ask Jackson: Is this airbreaks code?
    def get_motor_extension(self):
        servo_extension_position = 0
        return servo_extension_position # temporary change as needed

    def get_data_packet(self):
        return GraveDataPacket(position=self.get_motor_extension())
