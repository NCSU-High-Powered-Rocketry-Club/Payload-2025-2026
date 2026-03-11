"""General file for the data packet received from the zombie."""

import msgspec


class ZombieDataPacket(msgspec.Struct, tag=True, array_like=True):
    """Represents a data packet received from  Zombie."""

    soil_info: int

    # add more as needed
