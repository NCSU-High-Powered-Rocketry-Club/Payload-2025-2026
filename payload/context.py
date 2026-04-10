"""The context for the payload state machine."""

import threading
import time
from datetime import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from payload.data_handling.packets.context_data_packet import ContextDataPacket
from payload.data_handling.packets.grave_data_packet import GraveDataPacket
from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket
from payload.state import StandbyState

if TYPE_CHECKING:
    from firm_client import FIRMDataPacket

    from payload.base_classes.base_firm import BaseFIRM
    from payload.data_handling.logger import Logger
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
        "_deploy_thread",
        "_drilling_thread",
        "_legs_thread",
        "context_data_packet",
        "firm",
        "firm_data_packets",
        "grave",
        "grave_data_packet",
        "landing_time_seconds",
        "launch_time_seconds",
        "logger",
        "max_acceleration",
        "most_recent_firm_data_packet",
        "state",
        "total_acceleration",
        "zombie",
        "zombie_data_packet"
    )

    def __init__(
        self, grave: Grave | None, zombie: Zombie | None, firm: BaseFIRM, logger: Logger
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
        self.launch_time_seconds: int = 0
        self.total_acceleration: float = 0
        self.max_acceleration: float = 0
        self._deploy_thread: threading.Thread | None = None
        self._legs_thread: threading.Thread | None = None
        self._drilling_thread: threading.Thread | None = None
        self.landing_time_seconds: int = 0

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

        self.total_acceleration = ((self.most_recent_firm_data_packet.raw_acceleration_z_gs**2)
                + (self.most_recent_firm_data_packet.raw_acceleration_y_gs**2)
                + (self.most_recent_firm_data_packet.raw_acceleration_x_gs**2)
                ) ** 0.5

        self.max_acceleration = max(self.total_acceleration, self.max_acceleration)

        self.generate_data_packets()
        # TODO: Maybe change the fields in the context data packet

        self.logger.log(
            self.context_data_packet,
            self.firm_data_packets,
            self.grave_data_packet,
            self.zombie_data_packet,
        )

    def _run_in_thread(self, target, name: str) -> threading.Thread:
        """Runs a function in a daemon thread. Returns the thread so callers can track it."""
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()
        return thread

    def deploy_zombie(self):
        """
        Deploys Zombie out of the rocket. This method should only be called if code is Grave.
        """
        self._deploy_thread = self._run_in_thread(self.grave.deploy_zombie, "Deploy Zombie Thread")

    @property
    def is_deploy_complete(self) -> bool:
        return self._deploy_thread is not None and not self._deploy_thread.is_alive()

    def generate_data_packets(self) -> None:
        self.context_data_packet = ContextDataPacket(
            state=type(self.state),
            retrieved_firm_packets=len(self.firm_data_packets),
            update_timestamp_ns=int(time.time_ns()),
            epoch_time=datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M:%S"),
        )

        if self.grave:
            self.grave_data_packet = self.grave.get_data_packet()
            self.zombie_data_packet = ZombieDataPacket(0, 0, 0)

        if self.zombie:
            self.zombie_data_packet = self.zombie.get_data_packet()
            self.grave_data_packet = GraveDataPacket(0, 0)

    def deploy_zombie_legs(self) -> None:
        """Deploys zombie legs to stand it up. Only called if this is Zombie."""
        self._legs_thread = self._run_in_thread(self.zombie.deploy_legs, "Deploy Legs Thread")

    @property
    def is_legs_deployed(self) -> bool:
        return self._legs_thread is not None and not self._legs_thread.is_alive()

    def start_zombie_drilling(self) -> None:
        """Starts the drilling mechanism. Only called if this is Zombie."""
        self._drilling_thread = self._run_in_thread(self._drilling_sequence, "Drilling Thread")

    def _drilling_sequence(self):
        self.zombie.start_drilling()
        self.zombie.retract_with_motor()
        self.zombie.start_soil_sensor()
        self.zombie.stop_drilling()

    @property
    def is_drilling_complete(self) -> bool:
        return self._drilling_thread is not None and not self._drilling_thread.is_alive()

    @property
    def is_zombie_deployed(self) -> bool:
        return self.zombie.check_deployment() and self.zombie.check_orientation()

