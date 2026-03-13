"""
Real ZOMBIE test, calling zombie.py
"""

from payload.hardware.zombie import Zombie, INJORAServoDriver

def main():
    print("Initializing hardware drivers...")
    zombie = Zombie()

    print("Deploying Legs (hardware test)...")
    zombie.deploy_legs()

    print("Hardware test complete.")


if __name__ == "__main__":
    main()

    # on the pi, run python scripts/run_grave_hw_test.py
