import RPi.GPIO as GPIO
import time

# --------------------
# GPIO SETUP
# --------------------
PWM_PIN = 32      # PWM0
PWM_FREQ = 50     # 50 Hz for motor controller

GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)

pwm = GPIO.PWM(PWM_PIN, PWM_FREQ)
pwm.start(7.5)    # STOP signal

print("Motor initialized (STOP)")

try:
    # FORWARD
    print("Forward")
    pwm.ChangeDutyCycle(8.5)  # Adjust as needed
    time.sleep(3)

    # STOP
    print("Stop")
    pwm.ChangeDutyCycle(7.5)
    time.sleep(2)

    # REVERSE
    print("Reverse")
    pwm.ChangeDutyCycle(6.5)
    time.sleep(3)

    # STOP
    print("Stop")
    pwm.ChangeDutyCycle(7.5)
    time.sleep(2)

except KeyboardInterrupt:
    print("Interrupted")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up")


def ramp(pwm, start, end, step=0.05, delay=0.05):
    if start < end:
        value_range = [x * step for x in range(int(start/step), int(end/step)+1)]
    else:
        value_range = [x * step for x in range(int(start/step), int(end/step)-1, -1)]

    for dc in value_range:
        pwm.ChangeDutyCycle(dc)
        time.sleep(delay)

ramp(pwm, 7.5, 8.5)  # smooth forward
time.sleep(2)
ramp(pwm, 8.5, 7.5)  # smooth stop
