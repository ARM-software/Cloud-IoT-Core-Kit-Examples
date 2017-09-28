#!/usr/bin/env python

# Read photo resistor levels without an ADC by using a capacitor and counting the charges per cycle 
# based on https://learn.adafruit.com/basic-resistor-sensor-reading-on-raspberry-pi/basic-photocell-reading
# and this principal https://learn.adafruit.com/basic-resistor-sensor-reading-on-raspberry-pi
 
import RPi.GPIO as GPIO, time, os      
 
DEBUG = 1
GPIO.setmode(GPIO.BCM)
pin = 26
 
def RCtime (RCpin):
        reading = 0
        GPIO.setup(RCpin, GPIO.OUT)
        GPIO.output(RCpin, GPIO.LOW)
        time.sleep(0.1)
 
        GPIO.setup(RCpin, GPIO.IN)
        # This takes about 1 millisecond per loop cycle
        while (GPIO.input(RCpin) == GPIO.LOW):
                reading += 1
        return reading
 
while True:                                     
        print RCtime(pin)
