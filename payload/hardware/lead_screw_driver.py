"""General file for the lead screw driver."""

import time

import board
from digitalio import DigitalInOut, Direction


class LeadScrewDriver:
    """
    Driver for the lead screw.
    """

    def __init__(self, dir_pin=board.D27, step_pin=board.D22):
        self.dir = DigitalInOut(dir_pin)
        self.dir.direction = Direction.OUTPUT

        self.step = DigitalInOut(step_pin)
        self.step.direction = Direction.OUTPUT

    def extend(self, distance_mm):
        DISTANCE = distance_mm
        STEPS = int(DISTANCE / 0.01)

        microMode = 16
        steps = STEPS * microMode

        for _ in range(steps):
            self.step.value = True
            time.sleep(0.002)
            self.step.value = False
            time.sleep(0.002)

        time.sleep(1)
