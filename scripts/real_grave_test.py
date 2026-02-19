"""
Standalone hardware test for the Grave deployment system.
Runs on Raspberry Pi only.
"""

from payload.hardware.grave import Grave, ServoDriver, LeadScrewDriver


def main():
    print("Initializing hardware drivers...")
    grave = Grave()

    print("Deploying Zombie (hardware test)...")
    grave.deploy_zombie()

    print("Hardware test complete.")


if __name__ == "__main__":
    main()

    # on the pi, run python scripts/run_grave_hw_test.py
