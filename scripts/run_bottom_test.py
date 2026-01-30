import time
import pigpio
import RPi.GPIO as GPIO
from pymodbus.client import ModbusSerialClient
import board
import busio
import adafruit_ina260
from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# ==================================================
# ---------------- SERVO SETUP ---------------------
# ==================================================
SERVO_PIN = 13  # GPIO33 (pigpio numbering)

MIN_PULSE = 500
MID_PULSE = 1500
MAX_PULSE = 2500

SERVO_RUN_TIME = 1.0  # seconds to run 5-turn servo forward

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon")

# ==================================================
# ------------ PLANETARY MOTOR SETUP ---------------
# ==================================================
MOTOR_PWM_PIN = 12   # BCM numbering
Device.pin_factory = PiGPIOFactory()
motor = Servo(
    MOTOR_PWM_PIN,
    initial_value=0,
    min_pulse_width=1 / 1000,
    max_pulse_width=2 / 1000,
)

# ==================================================
# -------------- SOIL SENSOR SETUP -----------------
# ==================================================
client = ModbusSerialClient(
    port='/dev/serial0',   # CHANGE THIS IF NEEDED
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

# ==================================================
# ------------ CURRENT SENSOR SETUP ----------------
# ==================================================

# I2C setup
i2c = busio.I2C(board.SCL, board.SDA)

# INA260 object
ina260 = adafruit_ina260.INA260(i2c)

# ==================================================
# ----------------- FUNCTIONS ----------------------
# ==================================================
def run_servo_forward(duration):
    print("Running 5-turn servo forward")
    pi.set_servo_pulsewidth(SERVO_PIN, MAX_PULSE)
    # time.sleep(duration)

def stop_servo():
    pi.set_servo_pulsewidth(SERVO_PIN, MID_PULSE)
    print("Servo stopped")



def rotate_planetary_once_with_current():
    print("Rotating planetary motor")

    motor.value=-1

    start = time.time()
    while time.time() - start < 5.0:
        print(f"Current: {ina260.current:.1f} mA")
        time.sleep(0.1)

    motor.value=0
    print("Motor stopped")


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

        ecOutput = f"EC: {result.registers[0]} us/cm"
        
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



# ==================================================
# -------------------- MAIN -------------------------
# ==================================================
try:

    print("=== STARTING PAYLOAD SEQUENCE ===")
    # move lift servo to top
    pi.set_servo_pulsewidth(SERVO_PIN, MIN_PULSE)
    # turn off planetary motor
    motor.value=0
    time.sleep(2.0)
    print("starting drilling sequence")

    # start drilling
    motor.value = -.25
    time.sleep(0.5)

    pi.set_servo_pulsewidth(SERVO_PIN, 1250)

    time.sleep(4.0)


    print("drilling")
    time.sleep(0.5)

    pi.set_servo_pulsewidth(SERVO_PIN, MIN_PULSE)

    time.sleep(7.0)
    motor.value = 0
    print("drill complete")


    # # 1️⃣ Run 5-turn servo forward
    # run_servo_forward(SERVO_RUN_TIME)
    # time.sleep(1)

    # # 2️⃣ Rotate planetary gear motor once
    # rotate_planetary_once_with_current()
    # time.sleep(1)

    # 3️⃣ Soil sensor full readout
    print("Activating soil sensor...")

    if client.connect():
        print("Connected to Modbus RTU device.")

        for i in range(10):
            temp = readTemperature(client)
            moisture = readMoisture(client)
            ec = readECTest(client)
            pH = readpH(client)
            npk = readNPK(client)

            titleLine = "Soil Data"
            dashLine = "-------------------------"

            data = [titleLine, dashLine, temp, moisture, ec, pH] + npk + [dashLine]

            clearScreen()
            printData(data)
            time.sleep(0.25)

    else:
        print("Failed to connect to soil sensor.")
        print("Displaying dummy data...")
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

    print("=== SEQUENCE COMPLETE ===")

except KeyboardInterrupt:
    print("Sequence interrupted by user")

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, MIN_PULSE)
    motor.value = 0
    pi.stop()


    GPIO.cleanup()

    if client.connected:
        client.close()

    print("GPIO, pigpio, and Modbus cleaned up")
