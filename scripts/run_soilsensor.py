from pymodbus.client import ModbusSerialClient
from datetime import datetime
import pandas as pd
import time
import csv

def readMoisture(client):
    result = client.read_holding_registers(address=0x12, count=1, device_id=1)
    
    if result.isError():
        moistureLevelOutput = "error"
    else:
        result = result.registers[0]
    
        moistureLevel = result * 0.1
        moistureLevelOutput = f"Moisture: {moistureLevel}%"
    return moistureLevelOutput, moistureLevel
        
        
def readTemperature(client):
    result = client.read_holding_registers(address=0x13, count=1, device_id=1)
    
    if result.isError():
        tempOutput = "error"
    else:
        result = result.registers[0]
        
        temperatureC = result * 0.1
        temperatureF = temperatureC * (9/5) + 32
        
        tempOutput = f"Temperature: {temperatureF}\u00b0F/{temperatureC}\u00b0C"
        
    return tempOutput, temperatureF
        

def readEC(client):
    result1 = client.read_holding_registers(address=0x14, count=1, device_id=1)
    result2 = client.read_holding_registers(address=0x15, count=1, device_id=1)
    
    if result1.isError():
        ecOutput = "error"
    else:
        result1 = result1.registers[0] * 256
        result2 = result2.registers[0]
        
        
        ecOutput = f"EC: {result1 + result2} us/cm"
        
    return ecOutput

def readECTest(client):
    
    result = client.read_holding_registers(address=0x15, count=1, device_id=1)
    
    if result.isError():
        ecOutput = "error"
    else:
        #high_word = result.registers[0]  # register at 0x14
        #low_word = result.registers[1]   # register at 0x15

        #combined = (high_word << 16) | low_word  # shift high word 16 bits left, OR with low word
        ec = result.registers[0]
        ecOutput = f"EC: {result.registers[0]} us/cm"
        
    return ecOutput, ec
        
def readpH(client):
    result = client.read_holding_registers(address=0x06, count=1, device_id=1)

    if result.isError():
        pHOutput = "error"
    else:
        result = result.registers[0]
        
        pH = result * 0.01
        
        pHOutput = f"pH: {pH}"
    return pHOutput, pH    
        
def readNPK(client):
    result = client.read_holding_registers(address=0x1E, count=3, device_id=1)
    
    if result.isError():
        nitrogenOutput = "error"
        phosphorusOutput = "error"
        potassiumOutput = "error"
        
    else:
        nitrogenContent = result.registers[0]
        phosphorusContent = result.registers[1]
        potassiumContent = result.registers[2]
        
        nitrogenOutput = f"Nitrogen: {nitrogenContent} mg/kg"
        phosphorusOutput = f"Phosphorus: {phosphorusContent} mg/kg"
        potassiumOutput = f"Potassium: {potassiumContent} mg/kg"
        
    npkOutput = [nitrogenOutput, phosphorusOutput, potassiumOutput]
    npk = [nitrogenContent, phosphorusContent, potassiumContent]
    
    return npkOutput, npk
        
def printData(data):
    print("\n".join(data))
    
def clearScreen():
    for _ in range(10):
        # Move cursor up one line
        print("\033[F", end='')   # Equivalent to cursor up
        # Clear the line
        print("\033[K", end='')   # Equivalent to clear line
        # Move cursor back down
        print("\r", end='')
 
 
with open("Soil_Data_Test_Log.txt", mode="w") as soil_test_log_file:
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    soil_test_log_file.write(f"{timestamp}: Program Start\n")
      
    # Create the Modbus RTU client
    client = ModbusSerialClient(
        port='\dev\serial0',        # Virtual Serial Port that corresponds with UART Pins
        baudrate=9600,
        parity='N',
        stopbits=1,
        bytesize=8,
        timeout=1
    )

    # Connect to the slave device
    if client.connect():
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        soil_test_log_file.write(f"{timestamp}: Connected to soil sensor\n\n")
        
        print("Connected to Modbus RTU device.")
        
        # Open CSV for soil data "Soil_Data.csv"

        with open("Soil_Data.csv", mode="w", newline="") as soil_data_file:
            soil_writer = csv.writer(soil_data_file)
            soil_writer.writerow(["Temperature (F)", 
                            "Moisture (%)", 
                            "EC (us/cm)", 
                            "pH", 
                            "Nitrogen (mg/kg)",
                            "Phosphorus (mg/kg)",
                            "Potassium (mg/kg)"
                            ])
            try:
                for i in range(600):
                    temp_str, temp = readTemperature(client)
                    moisture_str, moisture = readMoisture(client)
                    ec_str, ec = readECTest(client)
                    pH_str, pH = readpH(client)
                    npk_str, npk = readNPK(client)
                    titleLine_str = "Soil Data"
                    dashLine_str = "-------------------------"
                    
                    # Log data to CSV
                    soil_writer.writerow([temp, moisture, ec, pH, npk[0], npk[1], npk[2]]);
                    
                    # Print data to command line
                    data = [titleLine_str, dashLine_str, temp_str, moisture_str, ec_str, pH_str] + npk_str + [dashLine_str]
                    #data = [titleLine, dashLine, ec, dashLine]
                    clearScreen()
                    
                    printData(data)
                    time.sleep(0.1)
                    
            except KeyboardInterrupt:
                print("\nTest Stopped")
        
        # Average Data and Log
        soilData = pd.read_csv("Soil_Data.csv")
        averageSoilData = soilData.mean(numeric_only=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        soil_test_log_file.write(f"{timestamp}: Data collection complete\n")
        soil_test_log_file.write(f"Temperature (F):    {averageSoilData['Temperature (F)']}\n")
        soil_test_log_file.write(f"Moisture (%):       {averageSoilData['Moisture (%)']}\n")
        soil_test_log_file.write(f"EC (us/cm):         {averageSoilData['EC (us/cm)']}\n")
        soil_test_log_file.write(f"pH:                 {averageSoilData['pH']}\n")
        soil_test_log_file.write(f"Nitrogen (mg/kg):   {averageSoilData['Nitrogen (mg/kg)']}\n")
        soil_test_log_file.write(f"Phosphorus (mg/kg): {averageSoilData['Phosphorus (mg/kg)']}\n")
        soil_test_log_file.write(f"Potassium (mg/kg):  {averageSoilData['Potassium (mg/kg)']}\n")
        
        
            
            
    else:
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        soil_test_log_file.write(f"\n{timestamp}: Failed to connect\n")
        print("Failed to connect.")
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    soil_test_log_file.write(f"{timestamp}: \nProgram Closed\n")
        
