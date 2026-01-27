import pigpio
import time

SERVO_PIN = 33  # GPIO33

pi = pigpio.pi()
if not pi.connected:
    raise RuntimeError("Could not connect to pigpio daemon")

# Typical servo pulse range (microseconds)
MIN_PULSE = 500     # full CCW
MID_PULSE = 1500    # center
MAX_PULSE = 2500    # full CW

try:
    print("Centering servo")
    pi.set_servo_pulsewidth(SERVO_PIN, MID_PULSE)
    time.sleep(2)

    print("Moving to min")
    pi.set_servo_pulsewidth(SERVO_PIN, MIN_PULSE)
    time.sleep(2)

    print("Moving to max")
    pi.set_servo_pulsewidth(SERVO_PIN, MAX_PULSE)
    time.sleep(2)

    print("Sweeping")
    for pw in range(MIN_PULSE, MAX_PULSE, 20):
        pi.set_servo_pulsewidth(SERVO_PIN, pw)
        time.sleep(0.02)

finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()