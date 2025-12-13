from firm_client import FIRMClient
import csv
from imu_logger import state
import math
import time
from datetime import datetime

# Initialize FIRM
firm = FIRMClient("/dev/ttyACM0")
firm.get_data_packets()
firm.zero_out_pressure_altitude()
firm.start()

# Open CSV file

def main():
    max_altitude = 0
    current_state = state.StandbyState()
    current_date = datetime.now()
    with open(f"Firm_Log_{current_date}.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time (s)", "State", "Altitude (m)", "Accel X (m/s^2)", "Accel Y (m/s^2)", "Accel Z (m/s^2)"])
        while True:
            # Get data packet from firm
            data = firm.get_data_packets(block=True)[-1]
            pressure = data.pressure_pascals
            temperature = data.temperature_celsius
            altitude = data.pressure_altitude_meters
            max_altitude = max(max_altitude, data.pressure_altitude_meters)

            current_state = current_state.update(data, max_altitude)
            
            # Log to CSV file WITH timestamps
            
            writer.writerow([data.timestamp_seconds, current_state.name, altitude, data.accel_x_meters_per_s2, data.accel_y_meters_per_s2, data.accel_z_meters_per_s2])

    
if __name__ == "__main__":
    main()
    firm.stop()
