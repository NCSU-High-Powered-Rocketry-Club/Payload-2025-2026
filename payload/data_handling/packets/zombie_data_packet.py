"""General file for the data packet received from the zombie."""

import msgspec


class ZombieDataPacket(msgspec.Struct, tag=True, array_like=True):
    """Represents a data packet received from  Zombie."""

    activating_legs: bool
    checking_orientation: bool
    nitrogen: float
    pH: float
    electrical_conductivity: float

    # add more as needed
