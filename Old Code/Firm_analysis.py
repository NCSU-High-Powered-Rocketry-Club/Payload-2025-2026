import pandas as pd
import matplotlib.pyplot as plt
#from firm import FIRM
import os
import numpy as np

firmdata = pd.read_csv('payload/imu_data.csv')
print(firmdata.head)

rx = np.array([[1,0,0],[0,0.707,-0.707],[0,0.707,0.707]])
ry = np.array([[0,0.707,0.707],[0,1,0],[-0.707,0.707,0]])
rz = np.array([[0.707,-0.707,0],[0.707,0.707,0],[0,0,1]])

az = firmdata['accel_y']*-0.707 + firmdata['accel_x']*-0.0707


plt.plot(firmdata['timestamp'],az, label='AccZ')
#plt.plot(firmdata['timestamp'], firmdata['accel_x'], label='AccX')
#plt.plot(firmdata['timestamp'], firmdata['accel_y'], label='AccY')
plt.plot(firmdata['timestamp'], firmdata['accel_z'], label='AccZold')
plt.xlabel("X-Axis Label")
plt.ylabel("Y-Axis Label")
plt.title("My First Graph")
plt.legend()
plt.show()