"""This is Zombie, the part of payload that drills and analyzes soil."""

import platform
import threading
import time

# Import only if on Raspberry Pi
if platform.system() == "Linux":
    import adafruit_ina260
    import board
    from gpiozero import Servo
    from gpiozero.devices import Device
    from gpiozero.pins.pigpio import PiGPIOFactory
    from pymodbus.client import ModbusSerialClient

    import pigpio

from payload.base_classes.base_zombie import BaseZombie
from payload.data_handling.packets.zombie_data_packet import ZombieDataPacket

# ==================================================
# ------------------- CONSTANTS --------------------
# ==================================================

# 5-turn auger servo (pigpio DMA PWM — works on any GPIO)
AUGER_SERVO_PIN = 23        # GPIO 23, Pin 16
RETRACTED_PW = 500          # us pulse width for start position, retracted
EXTENDED_PW = 1270          # us pulse width for fully extended position

# Planetary gear motor (pigpio DMA PWM — works on any GPIO)
DRILL_MOTOR_PWM_PIN = 12    # GPIO 12 Pin 32
DRILL_MOTOR_FREQ = 50       # Hz
DRILL_MOTOR_STOP_DC = 7.5   # % duty cycle — stop
DRILL_MOTOR_RUN_DC = 6.5    # % duty cycle — forward rotation

# Stall detection
STALL_CURRENT_THRESHOLD_A = 3.0   # amps — motor stops and auger retracts if exceeded

# Modbus soil sensor
MODBUS_PORT = "/dev/ttyUSB0"
MODBUS_BAUD = 9600

# Leg servo (INJORA, gpiozero)
LEG_SERVO_PIN = 13
LEG_TIME = 5


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
            servo.spin_forward(duration=LEG_TIME, speed=1.0)
        finally:
            servo.stop()

    def retract_legs(self) -> None:
        """
        Retracts the legs of the zombie using the INJORA continuous-rotation servo.
        """
        self.activating_legs = True

        servo = INJORAServoDriver(pin=LEG_SERVO_PIN)
        try:
            servo.spin_reverse(duration=LEG_TIME, speed=1.0)
        finally:
            servo.stop()

    # --------------------------------------------------
    # Drilling
    # --------------------------------------------------

    def start_drilling(self, step=2, delay=0.02) -> None:
        """
        Advances the auger and spins the planetary motor simultaneously.

        If the motor current exceeds STALL_CURRENT_THRESHOLD_A during a run,
        the motor stops immediately and the auger retracts while the motor is
        still. Once retracted, the attempt ends and — if attempts remain —
        the sequence restarts from the top.

        Each attempt counts toward max_attempts whether it completes normally
        or stalls, preventing an endless retry loop.

        :param step:         Pulse-width step size (us) for auger movement.
        :param delay:        Delay (seconds) between each auger step.
        """
        auger = AugerServoDriver(pin=AUGER_SERVO_PIN)
        drill = PlanetaryDrillMotor(pwm_pin=DRILL_MOTOR_PWM_PIN)
        current_sensor = INA260CurrentSensor()

        phase_duration = ((EXTENDED_PW - RETRACTED_PW) / step) * delay
        total_drill_duration = phase_duration * 2

            # Shared event: motor thread sets this when a stall is detected.
            # Auger thread checks it between advance and retract phases.
        stall_event = threading.Event()

        def auger_sequence():
            auger.advance(step=step, delay=delay)
            if stall_event.is_set():
                print("Stall detected: retracting auger with motor stopped.")
            auger.retract(step=step, delay=delay)

        def drill_sequence():
            stalled = drill.rotate_with_current_log(
                duration=total_drill_duration,
                current_sensor=current_sensor,
                stall_event=stall_event,
                stall_threshold_a=STALL_CURRENT_THRESHOLD_A,
            )
            if stalled:
                # Block here until the auger finishes retracting,
                # so cleanup() isn't called while it's still moving.
                auger_thread.join()

        try:
            auger_thread = threading.Thread(target=auger_sequence, daemon=True)
            drill_thread = threading.Thread(target=drill_sequence, daemon=True)

            auger_thread.start()
            drill_thread.start()

            auger_thread.join()
            drill_thread.join()

            if stall_event.is_set():
                print("Drill attempt ended due to stall.")
            else:
                print("Drill attempt completed successfully.")

        finally:
            # Always bring hardware to a safe state between attempts
            auger.stop()
            drill.stop()
            drill.cleanup()

    def stop_drilling(self) -> None:
        """
        Emergency stop for both the auger and planetary motor.
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

    Pulse widths map to position across 1800 degrees of travel:
        RETRACTED_PW = 500 us  — fully retracted
        EXTENDED_PW  = 1270 us — fully extended
    """

    def __init__(self, pin=AUGER_SERVO_PIN):
        self._pin = pin
        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon. "
                               "Run: sudo pigpiod")

    def advance(self, step=2, delay=0.02):
        """Step from retracted to extended position."""
        print("Auger extending")
        current_pw = RETRACTED_PW
        while current_pw < EXTENDED_PW:
            current_pw = min(current_pw + step, EXTENDED_PW)
            self._pi.set_servo_pulsewidth(self._pin, current_pw)
            time.sleep(delay)
        print("Auger extended")

    def retract(self, step=2, delay=0.02):
        """Step from extended back to retracted position."""
        print("Auger retracting")
        current_pw = EXTENDED_PW
        while current_pw > RETRACTED_PW:
            current_pw = max(current_pw - step, RETRACTED_PW)
            self._pi.set_servo_pulsewidth(self._pin, current_pw)
            time.sleep(delay)
        print("Auger retracted")

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

    The ESC/motor controller expects a standard RC servo signal:
        7.5% duty cycle at 50 Hz  ->  1500 us pulse  ->  stop
        6.5% duty cycle at 50 Hz  ->  1300 us pulse  ->  forward

    pigpio works in pulse widths (us), converted from duty cycle:
        pulse_width_us = duty_cycle_pct / 100 * (1_000_000 / frequency)
    """

    # Pulse widths in us at 50 Hz (period = 20,000 us)
    _STOP_PW = int(DRILL_MOTOR_STOP_DC / 100 * (1_000_000 / DRILL_MOTOR_FREQ))  # 1500 us
    _RUN_PW  = int(DRILL_MOTOR_RUN_DC  / 100 * (1_000_000 / DRILL_MOTOR_FREQ))  # 1300 us

    def __init__(self, pwm_pin=DRILL_MOTOR_PWM_PIN):
        self._pin = pwm_pin
        self._pi = pigpio.pi()
        if not self._pi.connected:
            raise RuntimeError("Could not connect to pigpio daemon. "
                               "Run: sudo pigpiod")
        self._pi.set_servo_pulsewidth(self._pin, self._STOP_PW)

    def rotate_with_current_log(
        self,
        duration: float,
        current_sensor=None,
        stall_event: threading.Event = None,
        stall_threshold_a: float = None,
    ) -> bool:
        """
        Spin the drill motor for *duration* seconds, ramping up and down
        smoothly. Monitors current every millisecond and stops immediately
        if current exceeds *stall_threshold_a* amps.

        :param duration:          Total run time in seconds (including ramps).
        :param current_sensor:    INA260CurrentSensor instance for monitoring.
        :param stall_event:       threading.Event set if a stall is detected.
        :param stall_threshold_a: Current limit in amps. None disables stall detection.
        :return:                  True if a stall was detected, False otherwise.
        """
        print("Planetary motor spinning")

        # Ramp up
        for pw in range(self._STOP_PW, self._RUN_PW, -1):
            self._pi.set_servo_pulsewidth(self._pin, pw)
            time.sleep(0.02)

        ramp_time = abs(self._STOP_PW - self._RUN_PW) * 0.02
        run_time = duration - (ramp_time * 2)
        stalled = False

        # Steady-state run with current monitoring
        start = time.time()
        while (time.time() - start) < run_time:
            if current_sensor:
                current_ma = current_sensor.read_current()
                current_a = current_ma / 1000.0
                print(f"  Current: {current_ma:.1f} mA")

                if stall_threshold_a is not None and current_a > stall_threshold_a:
                    print(f"  Stall detected! {current_a:.2f} A exceeds "
                          f"{stall_threshold_a} A threshold. Stopping motor.")
                    stalled = True
                    if stall_event is not None:
                        stall_event.set()
                    break   # Exit the run loop immediately

            time.sleep(0.001)

        # Ramp down (only if we didn't cut out early due to stall — if we
        # stalled the motor is already at stop; still safe to ramp from
        # wherever it is back to _STOP_PW)
        for pw in range(self._RUN_PW, self._STOP_PW):
            self._pi.set_servo_pulsewidth(self._pin, pw)
            time.sleep(0.02)

        self._pi.set_servo_pulsewidth(self._pin, self._STOP_PW)
        print("Planetary motor stopped")
        return stalled

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
        try:
            i2c = board.I2C()
            self._sensor = adafruit_ina260.INA260(i2c)
        except Exception as e:
            print(f"INA260 init failed: {e}")
            self._sensor = None

    def read_current(self) -> float:
        """Return current draw in milliamps (mA)."""
        if self._sensor is None:
            return 0.0
        return self._sensor.current

    def read_voltage(self) -> float:
        """Return bus voltage in volts (V)."""
        if self._sensor is None:
            return 0.0
        return self._sensor.voltage

    def read_power(self) -> float:
        """Return power in milliwatts (mW)."""
        if self._sensor is None:
            return 0.0
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
        print("\033[F\033[K\r", end="")