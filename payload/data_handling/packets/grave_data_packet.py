"""Grave data packet file for the data packet received from the grave."""

import msgspec


class GraveDataPacket(msgspec.Struct, tag=True, array_like=True):
    """Represents a data packet received from  Grave."""

    position: int
    latch: int

    # add more as needed
