import pandas as pd
import os
import time
import csv
from firm import FIRM

firm = FIRM("/path/to/device")  # e.g. "/dev/ttyUSB0" or "COM3"
firm.initialize()
data = f.get_most_recent_packets()
print(data[0].accel_x_meters_per_s2)


stopfunc = False
def check_time(data):
    if float(data["timestamp"]) > 10:
        return True
    
state = "Idle"
def get_state(row):
    acceleration = (row["accel_x"]**2 + row["accel_y"]**2 + row["accel_z"]**2)**0.5
    if "Prelaunch" == state and acceleration > 1.5:
        return "Launch"
    elif "Launch" == state and acceleration < 1:
        return "Coast"
    elif "Coast" == state and row["timestamp"] > 1000:
        return "Descent"
    elif "Descent" == state and acceleration > 0.9 and acceleration < 1.1:
        return "Landing"

output_file = 'Output.csv'

# If Output.csv already exists, delete it so we start fresh
if os.path.exists(output_file):
    os.remove(output_file)
print(data.head())
cols = list(data.columns) + ["state"]
print(cols)
pd.DataFrame(columns=cols).to_csv(output_file, mode = 'w', index=False, header=True)


for _, row in data.iterrows():
    row["state"] = get_state(row)
    row.to_frame().T.to_csv(output_file, mode='a', index=False, header=False)
