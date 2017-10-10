#!/usr/bin/python

# Connect the servo to 5v power and ground and the orange line to GPIO 18
# This utility code will run the servo through its full range of motion	

from subprocess import call
from time import sleep

pwmGPIO = "18"
pwmClock = "192"
pwmRange = "2000"
servoMin = 50
servoMax = 250
servoSteps = servoMax - servoMin
stepDelay = 0.01

#setup PWM for servo
err = call(["gpio", "-g", "mode", pwmGPIO, "pwm"])
err |= call(["gpio", "pwm-ms"])
err |= call(["gpio", "pwmc", pwmClock])
err |= call(["gpio", "pwmr", pwmRange])
if err != 0:
	print "gpio setup error:", err
	quit()
else:
	#move servo
	# call(["gpio", "-g", "pwm", pwmGPIO, str(servoMax)])
	# sleep(0.5)
	# call(["gpio", "-g", "pwm", pwmGPIO, str(servoMin)])
	# sleep(0.5)
	for step in range(0, servoSteps):
		#print step
		call(["gpio", "-g", "pwm", pwmGPIO, str(servoMin+step)])
		sleep(stepDelay)
	#sleep(0.5)
	for step in range(0, servoSteps):
		#print step
		call(["gpio", "-g", "pwm", pwmGPIO, str(servoMax-step)])
		sleep(stepDelay)

