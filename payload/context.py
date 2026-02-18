"""The context for the payload state machine."""

import time
from typing import TYPE_CHECKING

from payload.data_handling.packets.context_data_packet import ContextDataPacket
from payload.data_handling.packets.grave_data_packet import GraveDataPacket
from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket
from payload.state import StandbyState

if TYPE_CHECKING:
    from firm_client import FIRMDataPacket

    from payload.data_handling.logger import Logger
    from payload.hardware.firm import FIRM
    from payload.hardware.grave import Grave
    from payload.hardware.zombie import Zombie


class Context:
    """
    Manages the state machine for the rocket's payload system, keeping track of the current state,
    whether it's in grave or zombie mode, and communicating with hardware like the motor and FIRM.
    This class is what connects the state machine to the hardware.

    Both Grave and Zombie are running this code, but their state machines have different paths
    after landing is detected.

    Read more about the state machine pattern here:
    https://www.tutorialspoint.com/design_pattern/state_pattern.htm
    """

    __slots__ = (
        "context_data_packet",
        "firm",
        "firm_data_packets",
        "grave",
        "grave_data_packet",
        "logger",
        "most_recent_firm_data_packet",
        "state",
        "zombie",
        "zombie_data_packet",
    )

    def __init__(
        self, grave: Grave | None, zombie: Zombie | None, firm: FIRM, logger: Logger
    ) -> None:
        self.grave = grave
        self.zombie = zombie
        # This either has to be for Grave or for Zombie
        if (grave is None and zombie is None) or (grave is not None and zombie is not None):
            raise ValueError("This can either be a grave, or a zombie. Not both or neither.")

        self.logger = logger
        self.firm = firm
        self.state = StandbyState(self)
        self.firm_data_packets: list[FIRMDataPacket] = []
        self.most_recent_firm_data_packet: FIRMDataPacket | None = None
        self.context_data_packet: ContextDataPacket | None = None
        self.grave_data_packet: GraveDataPacket | None = None
        self.zombie_data_packet: ZombieDataPacket | None = None

    def start(self):
        self.firm.start()
        self.logger.start()

    def stop(self):
        self.firm.stop()
        self.logger.stop()

    def update(self):
        self.firm_data_packets = self.firm.get_data_packets()

        # If we don't have any packets, don't do anything
        if not self.firm_data_packets:
            return

        self.most_recent_firm_data_packet = self.firm_data_packets[-1]

        self.state.update()

        self.generate_data_packets()
        # TODO: Maybe change the fields in the context data packet

        self.logger.log(
            self.context_data_packet,
            self.firm_data_packets,
            self.grave_data_packet,
            self.zombie_data_packet,
        )

    # Ask Jackson about how this works
    def deploy_zombie(self):
        """
        Deploys Zombie out of the rocket. This method should only be called if code is Grave.
        """
        self.grave.deploy_zombie()

    def generate_data_packets(self) -> None:
        self.context_data_packet = ContextDataPacket(
            state=type(self.state),
            retrieved_firm_packets=len(self.firm_data_packets),
            update_timestamp_ns=int(time.time_ns()),
        )

        if self.grave:
            self.grave_data_packet = self.grave.get_data_packet()
            self.zombie_data_packet = ZombieDataPacket(0)

        if self.zombie:
            self.zombie_data_packet = self.zombie.get_data_packet()
            self.grave_data_packet = GraveDataPacket(0)
