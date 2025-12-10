#!/usr/bin/env python3

from firm import FIRM
import csv
import math

# Set constants
P0 = 101325 # Sea level atmospheric pressure

# Initialize FIRM
firm = FIRM(port="/dev/ttyACM0", baudrate=115200)
firm.initialize()


# Open CSV file
with open("Firm_Log.csv", mode="w", newline="") as file:
    writer = csv.writer(file)
    
    writer.writerow(["Time (s)", "Altitude (m)", "Accel X (m/s^2)", "Accel Y (m/s^2)", "Accel Z (m/s^2)"])
    
while True:
    # Get data packet from firm
    data = firm.get_most_recent_data_packet()
    pressure = data.pressure_pascals
    temperature = data.temperature_celsius
    
    pressureRatio = P0 / pressure
    eq1 = math.pow(pressureRatio,(1 / 5.257))
    eq2 = temperature + 273.15
    altitude = 44330*(1-eq1)
    
    # Log to CSV file WITH timestamps
    
    writer.writerow([data.timestamp_seconds, altitude, data.accel_x_meters_per_s2, data.accel_y_meters_per_s2, data.accel_z_meters_per_s2])

    