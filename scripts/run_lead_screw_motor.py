# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Use this example for digital pin control of an H-bridge driver
# like a DRV8833, TB6612 or L298N.

import time
import board
from digitalio import DigitalInOut, Direction

DELAY = 0.02
DISTANCE = 50 #mm
STEPS = int(DISTANCE / 0.01)

# You can use any available GPIO pin on both a microcontroller and a Raspberry Pi.
# The following pins are simply a suggestion. If you use different pins, update
# the following code to use your chosen pins.

# direction and step pins as outputs
DIR = DigitalInOut(board.D23)
DIR.direction = Direction.OUTPUT
STEP = DigitalInOut(board.D24)
STEP.direction = Direction.OUTPUT

# microstep mode, default is 1/16 so 16
# another ex: 1/4 microstep would be 4
microMode = 16
# full rotation multiplied by the microstep divider
steps = STEPS * microMode

DIR.value = not DIR.value
while True:
    # change direction every loop
    DIR.value = not DIR.value
    # toggle STEP pin to move the motor
    for i in range(steps):
        STEP.value = True
        time.sleep(0.002)
        STEP.value = False
        time.sleep(0.002)
    print("rotated! now reverse")
    # 1 second delay before starting again
    time.sleep(1)
