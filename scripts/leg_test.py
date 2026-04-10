"""
Leg testing for ZOMBIE
"""

from payload.hardware.zombie import Zombie, INJORAServoDriver

def main():
    print("Initializing hardware drivers...")
    zombie = Zombie()

    print("Retracting Legs (hardware test)...")
    zombie.retract_legs()

    print("Hardware test complete.")


if __name__ == "__main__":
    main()

    # on the pi, run python scripts/run_grave_hw_test.py