from firm import FIRM
import csv
from imu_logger import state
import math
import time

# Initialize FIRM
firm = FIRM(port="/dev/ttyAMA1")
firm.initialize()

# Open CSV file
with open("Firm_Log.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    
    writer.writerow(["Time (s)", "State", "Altitude (m)", "Accel X (m/s^2)", "Accel Y (m/s^2)", "Accel Z (m/s^2)"])
    
def main():
    max_altitude = 0
    current_state = state.StandbyState()
    while True:
        # Get data packet from firm
        data = firm.get_most_recent_data_packet()
        pressure = data.pressure_pascals
        temperature = data.temperature_celsius
        altitude = data.pressure_altitude_meters
        max_altitude = max(max_altitude, data.pressure_altitude_meters)

        current_state.update(data, max_altitude)
        
        # Log to CSV file WITH timestamps
        
        writer.writerow([data.timestamp_seconds, current_state.name, altitude, data.accel_x_meters_per_s2, data.accel_y_meters_per_s2, data.accel_z_meters_per_s2])

    
if __name__ == "__main__":
    main()