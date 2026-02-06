"""The constants for the payload."""

from pathlib import Path

# ------------------------ FIRM constants ------------------------

PORT = "COM6"
BAUD_RATE = 2_000_000
SERIAL_TIMEOUT_SECONDS = 1.0

# ------------------------ State machine constants ------------------------
LAUNCH_ALTITUDE_METERS = 200
LAUNCH_STATE_LENGTH_SECONDS = 345  # Lauren said main at crapogee would result in this descent time
GRAVE_DEPLOY_LENGTH_SECONDS = 10

# ------------------------ Zombie constants------------------------
# BCM numbering
DRILL_MOTOR_PIN = 12
LIFT_SERVO_PIN = 13

# Maximum microsecond ranges for the 5-turn lift servo.
LIFT_SERVO_MIN_PULSE = 500
LIFT_SERVO_MAX_PULSE = 2500


# -1 to reverse motor direction. This is simply multiplied by the motor input.
DRILL_SPIN_DIR = -1

# Speed, from 0 to 1, to spin the drill at.
DRILL_SPEED = 0.25

# The position to use for when the lift is in the highest position. (-1 to 1)
LIFT_UP_POSITION = -1

# The position to use for when the lift is in the down position. (-1 to 1)
LIFT_DOWN_POSITION = 0.375

# ---- Timings (in seconds) ----
# Time to wait before starting drilling.
DRILL_START_DELAY = 0.5

# Time to wait before plunging the drill into the ground
LIFT_START_DELAY = 0.5

# The time to wait for drilling to occur.
# NOTE: We have to wait for the lift to reach its "down" position, as well as
# wait a little bit longer for the auger to drill into the soil.
DRILL_TIME = 6.0

# Time to wait for the lift to come back up and deposit our soil inside.
RETRACTION_TIME = 7.0

# ------------------------ Grave constants------------------------


# ------------------------ Logger constants------------------------
LOGS_PATH = Path("logs")

LOG_BUFFER_SIZE = 5000
"""
Buffer size if CAPACITY is reached.

Once the state changes, this buffer will be logged to make sure we don't lose data.
"""

NUMBER_OF_LINES_TO_LOG_BEFORE_FLUSHING = 1000  # 1 second of data
"""
The number of lines we log before manually flushing the buffer and forcing the OS to write to the
file.
"""

STOP_SIGNAL = "STOP"
"""
The signal to stop the IMU, Logger, and ApogeePredictor thread, this will be put in the queue to
stop the threads.
"""
