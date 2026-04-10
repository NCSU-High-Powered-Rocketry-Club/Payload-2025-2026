"""This is Zombie, the part of payload that drills and analyzes soil."""

import platform
import threading
import time

# Import only if on Raspberry Pi
if platform.system() == "Linux":
    from adafruit_circuitpython_ina260 import adafruit_ina260
    import board
    import busio
    import pigpio
    from gpiozero import Servo
    from gpiozero.devices import Device
    from gpiozero.pins.pigpio import PiGPIOFactory
    from pymodbus.client import ModbusSerialClient

from payload.base_classes.base_zombie import BaseZombie
from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket

# ==================================================
# ------------------- CONSTANTS --------------------
# ==================================================

# 5-turn auger servo (pigpio DMA PWM — works on any GPIO)
AUGER_SERVO_PIN = 23        # GPIO 23, Pin 16
AUGER_MIN_PULSE = 500       # µs — full reverse
AUGER_MID_PULSE = 1500      # µs — stop
AUGER_MAX_PULSE = 2500      # µs — full forward
AUGER_RUN_TIME = 3.0        # seconds to run auger servo

# Planetary gear motor (pigpio DMA PWM — works on any GPIO)
DRILL_MOTOR_PWM_PIN = 12    # GPIO 12 Pin 32
DRILL_MOTOR_FREQ = 50       # Hz
DRILL_MOTOR_STOP_DC = 7.5   # % duty cycle — stop
DRILL_MOTOR_RUN_DC = 8.5    # % duty cycle — forward rotation

# Modbus soil sensor
MODBUS_PORT = "/dev/ttyUSB0"
MODBUS_BAUD = 9600

# Leg servo (INJORA, gpiozero)
LEG_SERVO_PIN = 13


# ==================================================
# -------------------- ZOMBIE ----------------------
# ==================================================

class Zombie(BaseZombie):
    """A class representing a zombie payload."""

    __slots__ = ("activating_legs", "checking_orientation", "soil_data")

    def __init__(self):
        self.activating_legs = 0
        self.checking_orientation = 0
        self.soil_data = 0

    # --------------------------------------------------
    # Leg Deployment
    # --------------------------------------------------

    def deploy_legs(self) -> None:
        """
        Deploys the legs of the zombie to stand it up using the INJORA
        continuous-rotation servo.
        """
        self.activating_legs = True

        servo = INJORAServoDriver(pin=LEG_SERVO_PIN)
        try:
            servo.spin_forward(duration=60, speed=1.0)
        finally:
            servo.stop()

    # --------------------------------------------------
    # Drilling
    # --------------------------------------------------

    def start_drilling(self) -> None:
        """
        Advances the auger and spins the planetary motor simultaneously.
        Both run for AUGER_RUN_TIME seconds, then both stop.
        """
        auger = AugerServoDriver(pin=AUGER_SERVO_PIN)
        drill = PlanetaryDrillMotor(pwm_pin=DRILL_MOTOR_PWM_PIN)
        current_sensor = INA260CurrentSensor()

        try:
            auger_thread = threading.Thread(
                target=auger.advance,
                kwargs={"duration": AUGER_RUN_TIME}
            )
            drill_thread = threading.Thread(
                target=drill.rotate_with_current_log,
                kwargs={"duration": AUGER_RUN_TIME, "current_sensor": current_sensor}
            )

            auger_thread.start()
            drill_thread.start()

            auger_thread.join()
            drill_thread.join()
        finally:
            auger.stop()
            drill.stop()
            drill.cleanup()

    def retract_with_motor(self, retract_duration=AUGER_RUN_TIME) -> None:
        """
        Retracts the auger while keeping the planetary motor spinning forward.
        Useful for pulling the drill bit back out of the soil after sampling.

        Both run for *retract_duration* seconds simultaneously, then both stop.

        :param retract_duration: How long to retract (seconds). Defaults to AUGER_RUN_TIME.
        """
        auger = AugerServoDriver(pin=AUGER_SERVO_PIN)
        drill = PlanetaryDrillMotor(pwm_pin=DRILL_MOTOR_PWM_PIN)
        current_sensor = INA260CurrentSensor()

        try:
            auger_thread = threading.Thread(
                target=auger.retract,
                kwargs={"duration": retract_duration}
            )
            drill_thread = threading.Thread(
                target=drill.rotate_with_current_log,
                kwargs={"duration": retract_duration, "current_sensor": current_sensor}
            )

            auger_thread.start()
            drill_thread.start()

            auger_thread.join()
            drill_thread.join()
        finally:
            auger.stop()
            drill.stop()
            drill.cleanup()

    def stop_drilling(self) -> None:
        """
        Emergency stop for both the auger and planetary motor.
        Note: start_drilling() and retract_with_motor() already stop
        hardware when they finish normally.
        """
        auger = AugerServoDriver(pin=AUGER_SERVO_PIN)
        drill = PlanetaryDrillMotor(pwm_pin=DRILL_MOTOR_PWM_PIN)
        try:
            auger.stop()
            drill.stop()
        finally:
            drill.cleanup()

    # --------------------------------------------------
    # Soil Sensor
    # --------------------------------------------------

    def start_soil_sensor(self) -> None:
        """
        Opens the Modbus connection to the soil sensor and runs a timed
        readout loop, printing results to the console. Reads for 120 s
        (480 samples x 0.25 s).
        """
        sensor = ModbusSoilSensor(port=MODBUS_PORT, baud=MODBUS_BAUD)

        if not sensor.connect():
            print("Failed to connect to soil sensor.")
            return

        try:
            print("Connected to Modbus RTU device.")
            for _ in range(480):
                data = sensor.read_all()
                _clear_screen()
                _print_data(data)
                time.sleep(0.25)
        finally:
            sensor.disconnect()

    # --------------------------------------------------
    # Deployment / Orientation Checks
    # --------------------------------------------------

    def check_deployment(self) -> bool:
        """
        Checks if the zombie deployment is complete.

        :return: True if deployment is complete, False otherwise.
        """
        return bool(self.activating_legs)

    def check_orientation(self) -> bool:
        """
        Checks if the zombie is upright.

        :return: True if the zombie is upright, False otherwise.
        """
        self.checking_orientation = True
        return True

    # --------------------------------------------------
    # Soil Data / Packet
    # --------------------------------------------------

    def get_soil_data(self):
        """Read a single snapshot of all soil metrics from the sensor."""
        sensor = ModbusSoilSensor(port=MODBUS_PORT, baud=MODBUS_BAUD)
        if not sensor.connect():
            return None
        try:
            return sensor.read_all()
        finally:
            sensor.disconnect()

    def get_data_packet(self):
        """Get the data packet for zombie. Includes soil sensor data."""
        self.soil_data = self.get_soil_data()
        return ZombieDataPacket(
            soil_info=self.soil_data,
            activating_legs=self.activating_legs,
            checking_orientation=self.checking_orientation,
        )

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def start(self) -> None:
        """Starts the zombie for processing data packets."""

    def stop(self) -> None:
        """Stops the zombie for processing data packets."""

    def update(self):
        pass

    def process_data_packet(self, data_packet):
        pass


# ==================================================
# ------------- LEG SERVO DRIVER -------------------
# ==================================================

class INJORAServoDriver:
    """
    Controller for the INJORA 35KG Digital Servo (360 Continuous Rotation).

    PWM spec: 1000 us (full reverse) / 1500 us (stop) / 2000 us (full forward).
    gpiozero Servo maps: value=-1 -> min_pulse, value=0 -> mid, value=1 -> max_pulse.
    """

    def __init__(self, pin=LEG_SERVO_PIN,
                 min_pwm_signal=0.001, max_pwm_signal=0.002):
        Device.pin_factory = PiGPIOFactory()
        self.servo = Servo(
            pin,
            min_pulse_width=min_pwm_signal,
            max_pulse_width=max_pwm_signal,
        )

    def stop(self):
        """Stop rotation and release torque."""
        self.servo.value = None

    def spin(self, duration, speed=1.0):
        """
        Spin the servo for a given duration at a given speed, then stop.

        :param duration: Seconds to spin (positive float).
        :param speed: Float from -1.0 (full reverse) to 1.0 (full forward).
        """
        if duration <= 0:
            raise ValueError("Duration must be a positive number")
        if not -1.0 <= speed <= 1.0:
            raise ValueError("Speed must be between -1.0 and 1.0")
        try:
            self.servo.value = speed
            time.sleep(duration)
        finally:
            self.stop()

    def spin_forward(self, duration, speed=1.0):
        """Spin forward for a given duration. Speed from 0.0 to 1.0."""
        if speed < 0:
            raise ValueError("Use spin_reverse() for reverse rotation")
        self.spin(duration, speed=abs(speed))

    def spin_reverse(self, duration, speed=1.0):
        """Spin in reverse for a given duration. Speed from 0.0 to 1.0."""
        if speed < 0:
            raise ValueError("Speed must be a positive value (0.0 to 1.0)")
        self.spin(duration, speed=-abs(speed))


# ==================================================
# ------------ AUGER SERVO DRIVER ------------------
# ==================================================

class AugerServoDriver:
    """
    Driver for the 5-turn auger servo using pigpio DMA-based PWM.

    pigpio's servo pulse control works on ANY GPIO pin, not just hardware
    PWM pins. It uses DMA to achieve ~1 us timing accuracy.

    Pulse widths: 500 us (full reverse) / 1500 us (stop) / 2500 us (full forward).
    """

    def __init__(self, pin=AUGER_SERVO_PIN):
        self._pin = pin
        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon. "
                               "Run: sudo pigpiod")

    def advance(self, duration=AUGER_RUN_TIME):
        """Run auger forward (into soil) for *duration* seconds, then stop."""
        print(f"Auger advancing for {duration} s")
        self._pi.set_servo_pulsewidth(self._pin, AUGER_MAX_PULSE)
        time.sleep(duration)
        self._pi.set_servo_pulsewidth(self._pin, AUGER_MID_PULSE)
        print("Auger stopped")

    def retract(self, duration=AUGER_RUN_TIME):
        """Run auger in reverse (out of soil) for *duration* seconds, then stop."""
        print(f"Auger retracting for {duration} s")
        self._pi.set_servo_pulsewidth(self._pin, AUGER_MIN_PULSE)
        time.sleep(duration)
        self._pi.set_servo_pulsewidth(self._pin, AUGER_MID_PULSE)
        print("Auger stopped")

    def stop(self):
        """Cut PWM signal to the auger servo and release pigpio resources."""
        self._pi.set_servo_pulsewidth(self._pin, 0)
        self._pi.stop()


# ==================================================
# ----------- PLANETARY DRILL MOTOR ----------------
# ==================================================

class PlanetaryDrillMotor:
    """
    Driver for the planetary gear motor using pigpio DMA-based PWM.

    Switching from RPi.GPIO to pigpio lets us use GPIO 32 (or any
    non-hardware-PWM pin) with stable, jitter-free pulse timing.

    The ESC/motor controller expects a standard RC servo signal:
        7.5% duty cycle at 50 Hz  ->  1500 us pulse  ->  stop
        8.5% duty cycle at 50 Hz  ->  1700 us pulse  ->  forward

    pigpio works in pulse widths (us), converted from duty cycle:
        pulse_width_us = duty_cycle_pct / 100 * (1_000_000 / frequency)
    """

    # Pulse widths in us at 50 Hz (period = 20,000 us)
    _STOP_PW = int(DRILL_MOTOR_STOP_DC / 100 * (1_000_000 / DRILL_MOTOR_FREQ))  # 1500 us
    _RUN_PW  = int(DRILL_MOTOR_RUN_DC  / 100 * (1_000_000 / DRILL_MOTOR_FREQ))  # 1700 us

    def __init__(self, pwm_pin=DRILL_MOTOR_PWM_PIN):
        self._pin = pwm_pin
        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon. "
                               "Run: sudo pigpiod")
        # Initialise to stop pulse
        self._pi.set_servo_pulsewidth(self._pin, self._STOP_PW)

    def rotate_with_current_log(self, duration=AUGER_RUN_TIME,
                                current_sensor=None):
        """
        Spin the drill motor forward for *duration* seconds, logging current
        every 100 ms via the supplied INA260CurrentSensor instance.
        """
        print("Planetary motor spinning")
        self._pi.set_servo_pulsewidth(self._pin, self._RUN_PW)

        start = time.time()
        while time.time() - start < duration:
            if current_sensor:
                print(f"  Current: {current_sensor.read_current():.1f} mA")
            time.sleep(0.1)

        self._pi.set_servo_pulsewidth(self._pin, self._STOP_PW)
        print("Planetary motor stopped")

    def stop(self):
        """Return motor to neutral (stop) pulse width."""
        self._pi.set_servo_pulsewidth(self._pin, self._STOP_PW)

    def cleanup(self):
        """Cut PWM signal and release pigpio resources."""
        self._pi.set_servo_pulsewidth(self._pin, 0)
        self._pi.stop()


# ==================================================
# ------------ INA260 CURRENT SENSOR ---------------
# ==================================================

class INA260CurrentSensor:
    """
    Thin wrapper around the Adafruit INA260 I2C current/power sensor.

    Hardware connections (fixed by the Pi's I2C bus — no pin constants needed):
        SDA  ->  GPIO 2  (Pin 3)
        SCL  ->  GPIO 3  (Pin 5)
        VCC  ->  3.3 V
        GND  ->  GND

    Enable I2C with: sudo raspi-config -> Interface Options -> I2C -> Enable
    """

    def __init__(self):
        i2c = board.I2C()  # automatically selects the correct hardware I2C bus
        self._sensor = adafruit_ina260.INA260(i2c)

    def read_current(self) -> float:
        """Return current draw in milliamps (mA)."""
        return self._sensor.current

    def read_voltage(self) -> float:
        """Return bus voltage in volts (V)."""
        return self._sensor.voltage

    def read_power(self) -> float:
        """Return power in milliwatts (mW)."""
        return self._sensor.power


# ==================================================
# ------------- MODBUS SOIL SENSOR -----------------
# ==================================================

class ModbusSoilSensor:
    """
    Driver for the RS-485 Modbus RTU soil sensor.

    Reads: moisture, temperature, EC, pH, and NPK from holding registers.
    """

    def __init__(self, port=MODBUS_PORT, baud=MODBUS_BAUD):
        self._client = ModbusSerialClient(
            port=port,
            baudrate=baud,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1,
        )

    def connect(self) -> bool:
        return self._client.connect()

    def disconnect(self):
        if self._client.connected:
            self._client.close()

    # ---------- individual register reads ----------

    def read_moisture(self) -> str:
        result = self._client.read_holding_registers(
            address=0x12, count=1, device_id=1)
        if result.isError():
            return "Moisture: error"
        return f"Moisture: {result.registers[0] * 0.1:.1f}%"

    def read_temperature(self) -> str:
        result = self._client.read_holding_registers(
            address=0x13, count=1, device_id=1)
        if result.isError():
            return "Temperature: error"
        temp_c = result.registers[0] * 0.1
        temp_f = temp_c * 9 / 5 + 32
        return f"Temperature: {temp_f:.1f}F / {temp_c:.1f}C"

    def read_ec(self) -> str:
        result = self._client.read_holding_registers(
            address=0x15, count=1, device_id=1)
        if result.isError():
            return "EC: error"
        return f"EC: {result.registers[0]} uS/cm"

    def read_ph(self) -> str:
        result = self._client.read_holding_registers(
            address=0x06, count=1, device_id=1)
        if result.isError():
            return "pH: error"
        return f"pH: {result.registers[0] * 0.01:.2f}"

    def read_npk(self) -> list[str]:
        result = self._client.read_holding_registers(
            address=0x1E, count=3, device_id=1)
        if result.isError():
            return ["Nitrogen: error", "Phosphorus: error", "Potassium: error"]
        n, p, k = result.registers
        return [
            f"Nitrogen:   {n} mg/kg",
            f"Phosphorus: {p} mg/kg",
            f"Potassium:  {k} mg/kg",
        ]

    # ---------- combined read ----------

    def read_all(self) -> list[str]:
        """Return a formatted list of all sensor readings."""
        header = ["Soil Data", "-------------------------"]
        readings = [
            self.read_temperature(),
            self.read_moisture(),
            self.read_ec(),
            self.read_ph(),
            *self.read_npk(),
        ]
        footer = ["-------------------------"]
        return header + readings + footer


# ==================================================
# --------------- DISPLAY HELPERS ------------------
# ==================================================

def _print_data(data: list[str]) -> None:
    print("\n".join(data))


def _clear_screen(lines: int = 10) -> None:
    for _ in range(lines):
        print("\033[F\033[K\r", end='')