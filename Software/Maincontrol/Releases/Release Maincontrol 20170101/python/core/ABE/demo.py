#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import RPi.GPIO as GPIO
import time
import threading

from ABE_ADCDifferentialPi import ADCDifferentialPi
from ABE_helpers import ABEHelpers



def init(PDI):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    
    i2c_helper = ABEHelpers()
    bus = i2c_helper.get_smbus()
    global adc
    adc = ADCDifferentialPi(bus, 0x68, 0x69, 18)
        
    global oldDi1
    oldDi1 = False

    
    #start asynchronous data collection as i2c reading takes long time and violets Yaha cycle time
    global u2
    i2cDataCollectionThread = threading.Thread(target=i2cDataCollection)
    i2cDataCollectionThread.start()


def update(PDI):
    global oldDi1
    global adc
    global u2
    
    PDI.count1 = PDI.count1 + 1

    if (PDI.count1 % 5 == 0):
        if (PDI.do1 == True):
            PDI.do1 = False
        else:
            PDI.do1 = True

        GPIO.output(12, PDI.do1)


    
    PDI.di1 = GPIO.input(16)
    if (PDI.di1 != oldDi1):
        oldDi1 = PDI.di1
        if (PDI.di1 == True):
            print('Input is HIGH')
        else:
            print('Input is LOW')
            
            
    r1 = 10000.0
    r2 = (u2 * r1) / (5 - u2)

    #print("R2: {0}V bei {1} Ohm".format(u2, r2))
    

def i2cDataCollection():
    global u2
    
    while (True):
        u2 = adc.read_voltage(4)
        # wait 0.5 seconds before reading the pins again
        time.sleep(0.5)    
            