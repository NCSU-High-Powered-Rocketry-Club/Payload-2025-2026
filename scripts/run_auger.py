import gpiozero
import time

servo = gpiozero.Servo(12, min_pulse_width=1/1000, max_pulse_width=2/1000)

servo.value = 0 # neutral

time.sleep(3)

servo.value = -1 # reverse
time.sleep(5)

servo.value = 0.5
time.sleep(2)

servo.value = 1 
time.sleep(5)


servo.value = 0
