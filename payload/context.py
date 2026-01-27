from firm_client import FIRMDataPacket

from payload.firm import FIRM
from payload.grave import Grave
from payload.state import StandbyState
from payload.zombie import Zombie


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

    # TODO add slots

    def __init__(self, grave: Grave | None, zombie: Zombie | None, firm: FIRM):
        self.grave = grave
        self.zombie = zombie

        # This either has to be for Grave or for Zombie
        if (grave is None and zombie is None) or (grave is not None and zombie is not None):
            raise ValueError("This can either be a grave, or a zombie. Not both or neither.")

        self.firm = firm
        self.state = StandbyState(self)
        self.firm_data_packets: list[FIRMDataPacket] = []
        self.most_recent_firm_data_packet: FIRMDataPacket | None = None

    def start(self):
        self.firm.start()

    def stop(self):
        self.firm.stop()

    def update(self):
        self.firm_data_packets = self.firm.get_data_packets()

        # If we don't have any packets, don't do anything
        if not self.firm_data_packets:
            return

        self.most_recent_firm_data_packet = self.firm_data_packets[-1]

        self.state.update()

        # TODO: do logging here (probably make a logger.py file to encapsulate that code)

    def deploy_zombie(self):
        """
        Deploys Zombie out of the rocket. This method should only be called if code is Grave.
        """
        self.grave.deploy_zombie()
