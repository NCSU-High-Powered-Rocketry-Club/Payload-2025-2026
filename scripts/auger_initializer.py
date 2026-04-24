import pigpio, time
pi = pigpio.pi()
pin = 23

pi.set_servo_pulsewidth(pin,1270)
time.sleep(2)
#print("Should have been still before this, moving now")
#pi.set_servo_pulsewidth(pin,1600)
#time.sleep(2)
#print("Fast done, starting slow")
#pi.set_servo_pulsewidth(pin,1550)
#time.sleep(2)
#print("Done with slow, stopping")
#pi.set_servo_pulsewidth(pin,0)
pi.stop()
#print("Done done")
