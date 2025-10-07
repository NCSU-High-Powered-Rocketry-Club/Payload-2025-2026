from pymodbus.client import ModbusSerialClient

# Create the Modbus RTU client
client = ModbusSerialClient(
    port='COM5',        # Replace with your actual port
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

# Connect to the slave device
if client.connect():
    print("Connected to Modbus RTU device.")

    # Read 2 holding registers starting at 0x12 (18 decimal)
    result = client.read_holding_registers(address=0x12, count=2, device_id=1)

    if result.isError():
        print("Error reading:", result)
    else:
        print("Moisture + Temp Register values:", result.registers)
        
    result = client.read_holding_registers(address=0x06, count=1, device_id=1)

    if result.isError():
        print("Error reading:", result)
    else:
        print("pH Register values:", result.registers)

    result = client.read_holding_registers(address=0x15, count=1, device_id=1)

    if result.isError():
        print("Error reading:", result)
    else:
        print("EC Register values:", result.registers)
        
    result = client.read_holding_registers(address=0x1E, count=3, device_id=1)

    if result.isError():
        print("Error reading:", result)
    else:
        print("NPK Register values:", result.registers)
        
    client.close()
else:
    print("Failed to connect.")
