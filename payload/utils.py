"""
File which contains utility functions which can be reused in the project.
"""

import queue
from typing import Any
import time
import board
from digitalio import DigitalInOut, Direction
from gpiozero import Device, Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import pigpio
import RPi.GPIO as GPIO
from pymodbus.client import ModbusSerialClient
import busio
import adafruit_ina260


def convert_unknown_type_to_float(obj_type: Any) -> float:
    """
    Converts the object to a float.

    Used by msgspec to convert numpy float64 to a float.
    :param obj_type: The object to convert.
    :return: The converted object.
    """
    return float(obj_type)


def convert_ns_to_s(nanoseconds: int) -> float:
    """
    Converts nanoseconds to seconds.

    :param nanoseconds: The time in nanoseconds.
    :return: The time in seconds.
    """
    return nanoseconds * 1e-9


def convert_s_to_ns(seconds: float) -> float:
    """
    Converts seconds to nanoseconds.

    :param seconds: The time in seconds.
    :return: The time in nanoseconds.
    """
    return seconds * 1e9


def get_all_packets_from_queue(packet_queue: queue.SimpleQueue, block: bool) -> list[Any]:
    """
    Empties the queue and returns all the items in a list.

    :param packet_queue: The queue to empty.
    :param block: Whether to block when getting items from the queue.

    :return: A list of all the items in the queue.
    """
    items = []

    if block:
        # Block until at least one item is available
        items.append(packet_queue.get(block=True))

    # Drain the rest of the queue, non-blocking
    while not packet_queue.empty():
        try:
            items.append(packet_queue.get(block=False))
        except queue.Empty:
            break
    return items


def deadband(input_value: float, threshold: float) -> float:
    """
    Returns 0.0 if input_value is within the deadband threshold.

    Otherwise, returns input_value adjusted by the threshold.
    :param input_value: The value to apply the deadband to.
    :param threshold: The deadband threshold.
    :return: Adjusted input_value or 0.0 if within the deadband.
    """
    if abs(input_value) < threshold:
        return 0.0
    return input_value


# Motor functions
def lead_screw_zombie(distance_mm: float, delay: float) -> None:
    """
    Run zombie lead screw. Distance is around 50mm, delay is around 0.002 s.
    """
    STEPS = int(distance_mm / 0.01)

    DIR = DigitalInOut(board.D23)
    DIR.direction = Direction.OUTPUT
    STEP = DigitalInOut(board.D24)
    STEP.direction = Direction.OUTPUT

    microMode = 16
    steps = STEPS * microMode

    DIR.value = not DIR.value
    while True:
        for i in range(steps):
            STEP.value = True
            time.sleep(delay)
            STEP.value = False
            time.sleep(delay)

def lead_screw_grave(distance_mm: float, delay: float) -> None:
    """
    Run zombie lead screw. Distance is around 467mm, delay is less than 0.002 s.
    """
    STEPS = int(distance_mm / 0.01)

    DIR = DigitalInOut(board.D17)
    DIR.direction = Direction.OUTPUT
    STEP = DigitalInOut(board.D27)
    STEP.direction = Direction.OUTPUT

    microMode = 16
    steps = STEPS * microMode

    DIR.value = not DIR.value

    for i in range(steps):
        STEP.value = True
        time.sleep(delay)
        STEP.value = False
        time.sleep(delay)

def latch_servo(delay: float) -> None:
    """
    Run the latch servo.
    """
    SERVO_PIN = 18
    Device.pin_factory = PiGPIOFactory()
    servo = Servo(SERVO_PIN, initial_value=0)

    # move to open the latch
    servo.min()
    time.sleep(delay)

    # move back to center
    servo.mid()
    time.sleep(delay)

    servo.detach()


def run_zombie_bottom() -> None:
    """
    Run zombie auger and rack and pinion and soil sensor.
    """
    SERVO_PIN = 33  # GPIO33 (pigpio numbering)

    MIN_PULSE = 500
    MID_PULSE = 1500
    MAX_PULSE = 2500

    SERVO_RUN_TIME = 3.0  # seconds to run 5-turn servo forward

    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError("Could not connect to pigpio daemon")

    # ==================================================
    # ------------ PLANETARY MOTOR SETUP ---------------
    # ==================================================
    MOTOR_PWM_PIN = 32   # BCM numbering
    MOTOR_FREQ = 50

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MOTOR_PWM_PIN, GPIO.OUT)

    motor_pwm = GPIO.PWM(MOTOR_PWM_PIN, MOTOR_FREQ)
    motor_pwm.start(7.5)  # STOP

    # ==================================================
    # -------------- SOIL SENSOR SETUP -----------------
    # ==================================================
    client = ModbusSerialClient(
        port='/dev/ttyUSB0',   # CHANGE THIS IF NEEDED
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
        time.sleep(duration)
        pi.set_servo_pulsewidth(SERVO_PIN, MID_PULSE)
        print("Servo stopped")

    def rotate_planetary_once_with_current():
        print("Rotating planetary motor")

        motor_pwm.ChangeDutyCycle(8.5)

        start = time.time()
        while time.time() - start < 1.0:
            print(f"Current: {ina260.current:.1f} mA")
            time.sleep(0.1)

        motor_pwm.ChangeDutyCycle(7.5)
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

        # 1️⃣ Run 5-turn servo forward
        run_servo_forward(SERVO_RUN_TIME)
        time.sleep(1)

        # 2️⃣ Rotate planetary gear motor once
        rotate_planetary_once_with_current()
        time.sleep(1)

        # 3️⃣ Soil sensor full readout
        print("Activating soil sensor...")

        if client.connect():
            print("Connected to Modbus RTU device.")

            for i in range(480):
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

            for i in range(100):
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

    finally:
        pi.set_servo_pulsewidth(SERVO_PIN, 0)
        pi.stop()

        motor_pwm.stop()
        GPIO.cleanup()

        if client.connected:
            client.close()

        print("GPIO, pigpio, and Modbus cleaned up")
