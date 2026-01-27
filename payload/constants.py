"""The constants for the payload."""

# FIRM constants

PORT = "COM5"
BAUD_RATE = 2_000_000
SERIAL_TIMEOUT_SECONDS = 1.0

# State machine constants
LAUNCH_ALTITUDE_METERS = 200
LAUNCH_STATE_LENGTH_SECONDS = 345  # Lauren said main at crapogee would result in this descent time
GRAVE_DEPLOY_LENGTH_SECONDS = 10

# Servo constants
ServoExtension = None

# logger constants
IDLE_LOG_CAPACITY = 5000  # Using the formula above, this is 5 seconds of data
"""
The maximum number of data packets to log in the StandbyState and LandedState.

This is to prevent log file sizes from growing too large. Some of our 2023-2024 launches were >300
mb.
"""
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
