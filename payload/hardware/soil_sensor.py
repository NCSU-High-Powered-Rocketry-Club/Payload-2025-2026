from pymodbus.client import ModbusSerialClient

from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket


class SoilSensor:
    def __init__(self) -> None:
        # Soil sensor initialization
        self.client = ModbusSerialClient(
            port='/dev/ttyUSB0',   # CHANGE THIS IF NEEDED
            baudrate=9600,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )

    def readMoisture(self):
        result = self.client.read_holding_registers(address=0x12, count=1, device_id=1)
        
        if result.isError():
            moistureLevelOutput = -1
        else:
            result = result.registers[0]
        
            moistureLevel = result * 0.1
            #moistureLevelOutput = f"Moisture: {moistureLevel}%"
        return moistureLevel
            
            
    def readTemperature(self):
        result = self.client.read_holding_registers(address=0x13, count=1, device_id=1)
        
        if result.isError():
            tempOutput = -100
        else:
            result = result.registers[0]
            
            temperatureC = result * 0.1
            temperatureF = temperatureC * (9/5) + 32
            
            #tempOutput = f"Temperature: {temperatureF}\u00b0F/{temperatureC}\u00b0C"
            
        return temperatureF

    def readEC(self):
        
        result = self.client.read_holding_registers(address=0x15, count=1, device_id=1)
        
        if result.isError():
            ecOutput = -1
        else:
            #high_word = result.registers[0]  # register at 0x14
            #low_word = result.registers[1]   # register at 0x15

            #combined = (high_word << 16) | low_word  # shift high word 16 bits left, OR with low word

            # ecOutput = f"EC: {result.registers[0]} us/cm"
            ecOutput = result.registers[0]
            
        return ecOutput
            
    def readpH(self):
        result = self.client.read_holding_registers(address=0x06, count=1, device_id=1)

        if result.isError():
            pHOutput = -1
        else:
            result = result.registers[0]
            
            pH = result * 0.01
            
            # pHOutput = f"pH: {pH}"
            pHOutput = pH
        return pHOutput    
            
    def readNPK(self):
        result = self.client.read_holding_registers(address=0x1E, count=3, device_id=1)
        
        if result.isError():
            nitrogenOutput = -1
            phosphorusOutput = -1
            potassiumOutput = -1
            
        else:
            nitrogenContent = result.registers[0]
            phosphorusContent = result.registers[1]
            potassiumContent = result.registers[2]
            
            # nitrogenOutput = f"Nitrogen: {nitrogenContent} mg/kg"
            # phosphorusOutput = f"Phosphorus: {phosphorusContent} mg/kg"
            # potassiumOutput = f"Potassium: {potassiumContent} mg/kg"

            nitrogenOutput = nitrogenContent
            phosphorusOutput = phosphorusContent
            potassiumOutput = potassiumContent
            
        npkOutput = (nitrogenOutput, phosphorusOutput, potassiumOutput)
        
        return npkOutput
            
    def printData(self, data):
        print("\n".join(data))

    def readAll(self):
        return ZombieDataPacket(
         self.readTemperature(),
         self.readMoisture(),
         self.readEC(),
         self.readpH(),
         *self.readNPK()
        )
