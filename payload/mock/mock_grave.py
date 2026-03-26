"""Mock Grave code."""
import time

from payload.base_classes.base_grave import BaseGrave
from payload.data_handling.packets.grave_data_packet import GraveDataPacket


class MockGrave(BaseGrave):
    """
    High-level controller for the Grave deployment system.
    """

    __slots__ = ("deployed", "latch_state", "ejecting_zombie",)

    def __init__(self):
        self.deployed = False
        self.latch_state = False
        self.ejecting_zombie = False

    def start(self):
        pass

    def update(self):
        if not self.deployed:
            self.deploy_zombie()
            self.deployed = True

    def stop(self):
        pass

    def deploy_zombie(self):
        self.latch_state = True
        time.sleep(5)
        self.ejecting_zombie = True

    def get_data_packet(self):
        return GraveDataPacket(ejecting_zombie=self.ejecting_zombie, latch=self.latch_state)
