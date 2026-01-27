"""
The main file which will be run on the Raspberry Pi.

It will create the Context object and run the main loop.
"""

from payload.context import Context
from payload.hardware.grave import Grave
from payload.hardware.firm import FIRM
from payload.hardware.zombie import Zombie


# TODO: eventually add more stuff here like the logger
def create_components() -> tuple[FIRM]:
    """Creates the system components needed for the payload system."""
    firm = FIRM()

    return (firm,)


def run_grave():
    """Runs the code for Grave."""
    firm = create_components()[0]
    grave = Grave()
    run_flight_loop(Context(grave=grave, zombie=None, firm=firm))


def run_zombie():
    """Runs the code for Zombie."""
    firm = create_components()[0]
    zombie = Zombie()
    run_flight_loop(Context(grave=None, zombie=zombie, firm=firm))


def run_flight_loop(context: Context):
    """Runs the main loop for the code."""
    try:
        context.start()
        while True:
            context.update()
    except KeyboardInterrupt:
        # Maybe do stuff here eventually
        pass
    finally:
        context.stop()
