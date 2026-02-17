"""
The main file which will be run on the Raspberry Pi.

It will create the Context object and run the main loop.
"""

from payload.constants import LOGS_PATH
from payload.context import Context
from payload.data_handling.logger import Logger
from payload.hardware.firm import FIRM
from payload.hardware.grave import Grave
from payload.hardware.latch_driver import ServoDriver
from payload.hardware.lead_screw_driver import LeadScrewDriver
from payload.hardware.zombie import Zombie


# TODO: eventually add more stuff here like the logger
def create_components() -> tuple[FIRM, Logger]:
    """Creates the system components needed for the payload system."""
    firm = FIRM()
    logger = Logger(LOGS_PATH)
    return firm, logger


def run_grave():
    """Runs the code for Grave."""
    firm, logger = create_components()

    # Instantiate hardware drivers
    servo_driver = ServoDriver()
    lead_screw_driver = LeadScrewDriver()

    # Inject them into Grave
    grave = Grave(servo_driver=servo_driver, lead_screw_driver=lead_screw_driver)

    run_flight_loop(Context(grave=grave, zombie=None, firm=firm, logger=logger))


def run_zombie():
    """Runs the code for Zombie."""
    firm, logger = create_components()
    zombie = Zombie()
    run_flight_loop(Context(grave=None, zombie=zombie, firm=firm, logger=logger))


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
