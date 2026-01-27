import RPi.GPIO as GPIO
import time

# --------------------
# GPIO SETUP
# --------------------
SERVO_PIN = 18     # GPIO pin connected to servo signal
PWM_FREQ = 50      # Standard servo frequency

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, PWM_FREQ)
pwm.start(7.5)     # Center position

print("Servo initialized at center")

try:
    while True:
        print("Move to LEFT")
        pwm.ChangeDutyCycle(5.5)
        time.sleep(2)

        print("Center")
        pwm.ChangeDutyCycle(7.5)
        time.sleep(2)

        print("Move to RIGHT")
        pwm.ChangeDutyCycle(9.5)
        time.sleep(2)

        print("Center")
        pwm.ChangeDutyCycle(7.5)
        time.sleep(2)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    pwm.stop()
    GPIO.cleanup()
    print("GPIO cleaned up")