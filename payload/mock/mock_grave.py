"""Mock Grave code."""
import time

from payload.base_classes.base_grave import BaseGrave
from payload.data_handling.packets.grave_data_packet import GraveDataPacket


class MockGrave(BaseGrave):
    """
    High-level controller for the Grave deployment system.
    """

    __slots__ = ("deployed", "latch_state", "motor_extension",)

    def __init__(self):
        self.deployed = False
        self.latch_state = 0
        self.motor_extension = 0

    def start(self):
        pass

    def update(self):
        if not self.deployed:
            self.deploy_zombie()
            self.deployed = True

    def stop(self):
        pass

    def deploy_zombie(self):
        self.latch_state = 1
        time.sleep(2)
        self.motor_extension = 1

    def get_data_packet(self):
        return GraveDataPacket(position=self.motor_extension, latch=self.latch_state)
