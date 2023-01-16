#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO ## Import GPIO Library
import time ## Import 'time' library.  Allows us to use 'sleep'

GPIO.setmode(GPIO.BOARD) ## Use BOARD pin numbering
GPIO.setup(11, GPIO.OUT) ## Setup GPIO pin 17 to OUT

## Define function named Blink()
def Blink(numTimes, speed):
    for i in range(0,numTimes): ## Run loop numTimes
        print ("Iteration " + str(i+1)) ##Print current loop
        GPIO.output(11, GPIO.HIGH) ## Turn on GPIO pin 17
        time.sleep(speed) ## Wait
        GPIO.output(11, GPIO.LOW) ## Switch off GPIO pin 17
        time.sleep(speed) ## Wait
    print ("Done") ## When loop is complete, print "Done"
    GPIO.cleanup()

## Prompt user for input
iterations = 10 #total number of times to blink
speed = 1 # Enter the length of each blink in seconds

## Start Blink() function. Convert user input from strings to numeric data types and pass to Blink() as parameters
Blink(int(iterations),float(speed))
        