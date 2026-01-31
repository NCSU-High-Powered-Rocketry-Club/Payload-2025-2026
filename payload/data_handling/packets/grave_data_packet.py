"""

"""

import msgspec

class GraveDataPacket(msgspec.Struct, tag=True, array_like=True):
    """Represents a data packet received from  Grave"""

    position: int

    # add more as needed
