"""General file for the data packet received from the zombie."""

import msgspec


class ZombieDataPacket(msgspec.Struct, tag=True, array_like=True):
    """Represents a data packet received from  Zombie."""

    moisture : float
    temperature : float
    ec : float
    pH : float
    npk_nitrogen : float
    npk_phosphorus : float
    npk_potassium : float

