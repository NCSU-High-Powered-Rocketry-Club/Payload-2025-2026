import pandas as pd
import os
import time
import csv


stopfunc = False
def check_time(data):
    if float(data["timestamp"]) > 10:
        return True
    
state = "Prelaunch"
def get_state(row):
    acceleration = (row["accel_x"]**2 + row["accel_y"]**2 + row["accel_z"]**2)**0.5
    if "Prelaunch" == state and acceleration > 1.5:
        takeoff = row["timestamp"]
        return "Launch"
    elif "Launch" == state and acceleration < 0 or row["timestamp"] - takeoff > 2.5:
        return "Coast"
    elif "Coast" == state and row["timestamp"] > 1000 or row["timestamp"] - takeoff > 11.5:
        return "Descent"
    elif "Descent" == state and acceleration > 0 or row["timestamp"] - takeoff > 65:
        return "Landing"

data = pd.read_csv('payload/imu_data.csv')
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
