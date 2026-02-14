"""
Standalone hardware test for the Grave deployment system.
Runs on Raspberry Pi only.
"""

from payload.hardware.grave import Grave
from payload.hardware.latch_driver import ServoDriver
from payload.hardware.lead_screw_driver import LeadScrewDriver


def main():
    print("Initializing hardware drivers...")

    servo = ServoDriver()
    lead_screw = LeadScrewDriver()

    grave = Grave(
        servo_driver=servo,
        lead_screw_driver=lead_screw
    )

    print("Deploying Zombie (hardware test)...")
    grave.deploy_zombie()

    print("Hardware test complete.")


if __name__ == "__main__":
    main()

    # on the pi, run python scripts/run_grave_hw_test.py
