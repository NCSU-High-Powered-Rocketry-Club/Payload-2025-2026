from pymodbus.client import ModbusSerialClient
import time

def readMoisture(client):
    result = client.read_holding_registers(address=0x12, count=1, device_id=1)
    
    if result.isError():
        moistureLevelOutput = "error"
    else:
        result = result.registers[0]
    
        moistureLevel = result * 0.1
        moistureLevelOutput = f"Moisture: {moistureLevel}%"
    return moistureLevelOutput
        
        
def readTemperature(client):
    result = client.read_holding_registers(address=0x13, count=1, device_id=1)
    
    if result.isError():
        tempOutput = "error"
    else:
        result = result.registers[0]
        
        temperatureC = result * 0.1
        temperatureF = temperatureC * (9/5) + 32
        
        tempOutput = f"Temperature: {temperatureF}\u00b0F/{temperatureC}\u00b0C"
        
    return tempOutput
        

def readEC(client):
    result = client.read_holding_registers(address=0x15, count=1, device_id=1)
    
    if result.isError():
        ecOutput = "error"
    else:
        result = result.registers[0]
        
        ecOutput = f"EC: {result} us/cm"
        
    return ecOutput
        
def readpH(client):
    result = client.read_holding_registers(address=0x06, count=1, device_id=1)

    if result.isError():
        pHOutput = "error"
    else:
        result = result.registers[0]
        
        pH = result * 0.01
        
        pHOutput = f"pH: {pH}"
    return pHOutput    
        
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
    
    return npkOutput
        
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

    for i in range(480):
        temp = readTemperature(client)
        moisture = readMoisture(client)
        ec = readEC(client)
        pH = readpH(client)
        npk = readNPK(client)
        titleLine = "Soil Data"
        dashLine = "-------------------------"
        
        data = [titleLine, dashLine, temp, moisture, ec, pH] + npk + [dashLine]
        
        clearScreen()
        
        printData(data)
        time.sleep(0.25)
        
        
        
else:
    print("Failed to connect.")
    
    for i in range(1200):
        temp = f"Num {1 + i}"
        moisture = f"Crazy {2 - (i / 2)}"
        ec = f"Hot {10 * i}"
        pH = f"Easy {4 - i}"
        npk = f"Spaghetti {5 - (2 * i)}"
        titleLine = "Soil Data"
        dashLine = "-------------------------"
        
        data = [titleLine, dashLine, temp, moisture, ec, pH, npk, dashLine]
        
        printData(data)
        time.sleep(0.1)
        clearScreen()
