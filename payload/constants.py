"""The constants for the payload."""

# FIRM constants

PORT = "COM5"
BAUD_RATE = 2_000_000
SERIAL_TIMEOUT_SECONDS = 1.0

# State machine constants
LAUNCH_ALTITUDE_METERS = 200
LAUNCH_STATE_LENGTH_SECONDS = 345  # Lauren said main at crapogee would result in this descent time
GRAVE_DEPLOY_LENGTH_SECONDS = 10
