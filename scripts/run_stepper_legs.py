# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Use this example for digital pin control of an H-bridge driver
# like a DRV8833, TB6612 or L298N.

import time

import board
import digitalio

from adafruit_motor import stepper

DELAY = 0.02
DISTANCE = 40 #mm
STEPS = int(DISTANCE / 0.01)

# You can use any available GPIO pin on both a microcontroller and a Raspberry Pi.
# The following pins are simply a suggestion. If you use different pins, update
# the following code to use your chosen pins.



# To use with a Raspberry Pi:
coils = (
    digitalio.DigitalInOut(board.D5),  # A1
    digitalio.DigitalInOut(board.D6),  # A2
    digitalio.DigitalInOut(board.D24),  # B1
    digitalio.DigitalInOut(board.D23),  # B2
    )

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

motor = stepper.StepperMotor(coils[0], coils[1], coils[2], coils[3], microsteps=None)

# LEG DOWN
for step in range(STEPS):
    motor.onestep(direction=stepper.BACKWARD)
    time.sleep(DELAY)
   
#LEG UP 
for step in range(STEPS):
    motor.onestep(direction=stepper.BACKWARD)
    time.sleep(DELAY)


motor.release()
