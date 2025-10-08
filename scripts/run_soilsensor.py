from pymodbus.client import ModbusSerialClient
import time

def readMoisture(client):
    result = client.read_holding_registers(address=0x12, count=1, device_id=1)
    
    if result.isError():
        print("Error Reading: ", result)
    else:
        result = result.registers.index(0)
    
        moistureLevel = result * 0.1
        print("Moisture: ", moistureLevel, "%")
        
        
def readTemperature(client):
    result = client.read_holding_registers(address=0x13, count=1, device_id=1)
    
    if result.isError():
        print("Error Reading: ", result)
    else:
        result = result.registers.index(0)
        
        temperatureC = result * 0.1
        temperatureF = temperatureC * (9/5) + 32
        
        print("Temperature: ", temperatureF, "\u00b0F/", temperatureC, "\u00b0C")
        

def readEC(client):
    result = client.read_holding_registers(address=0x15, count=1, device_id=1)
    
    if result.isError():
        print("Error Reading: ", result)
    else:
        result = result.registers.index(0)
        
        print("EC: ", result, " us/cm")
        
def readpH(client):
    result = client.read_holding_registers(address=0x06, count=1, device_id=1)

    if result.isError():
        print("Error Reading: ", result)
    else:
        result = result.registers.index(0)
        
        pH = result * 0.01
        
        print("pH: ", pH)
        
def readNPK(client):
    result = client.read_holding_registers(address=0x1E, count=3, device_id=1)
    
    if result.isError():
        print("Error Reading: ", result)
    else:
        nitrogenContent = result.registers.index(0)
        phosphorusContent = result.registers.index(1)
        potassiumContent = result.registers.index(2)
        
        print("Nitrogen:   ", nitrogenContent, "mg/kg")
        print("Phosphorus: ", phosphorusContent, "mg/kg")
        print("Potassium:  ", potassiumContent, "mg/kg")
        
        




# Determine correct port ID
comPort = input("Enter COM Port: ")


# Create the Modbus RTU client
client = ModbusSerialClient(
    port=comPort,        # Replace with your actual port
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

# Connect to the slave device
if client.connect():
    print("Connected to Modbus RTU device.")

    for i in range(120):
        readTemperature(client)
        readMoisture(client)
        readEC(client)
        readpH(client)
        readNPK(client)
        
        time.sleep(1)
        
else:
    print("Failed to connect.")
