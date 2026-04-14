"""
Real ZOMBIE hardware test — calls all Zombie methods in sequence.

Run on the Pi with: uv run scripts/real_zombie_test.py
"""

from payload.hardware.zombie import Zombie


def main():
    print("  ZOMBIE HARDWARE TEST")

    zombie = Zombie()

    # 1. Deploy legs (INJORA continuous-rotation servo)
    print("\n[1/5] Deploying legs...")
    zombie.deploy_legs()

    # 2. Check deployment state
    print("\n[2/5] Checking deployment...")
    deployed = zombie.check_deployment()
    print(f"      Deployment complete: {deployed}")

    # 3. Check orientation (IMU / placeholder)
    print("\n[3/5] Checking orientation...")
    upright = zombie.check_orientation()
    print(f"      Zombie upright: {upright}")

    # 4. Drill — advances auger servo then spins planetary motor
    print("\n[4/5] Starting drilling sequence...")
    zombie.start_drilling()
    print("      Drilling complete.")

    # 5. Read soil sensor for full timed session
    print("\n[5/5] Starting soil sensor readout...")
    zombie.start_soil_sensor()
    print("      Soil sensor readout complete.")

    # Optional: grab a single data packet
    print("\nFetching final data packet...")
    packet = zombie.get_data_packet()
    print(f"      Packet: {packet}")

    print("  HARDWARE TEST COMPLETE")


if __name__ == "__main__":
    main()
