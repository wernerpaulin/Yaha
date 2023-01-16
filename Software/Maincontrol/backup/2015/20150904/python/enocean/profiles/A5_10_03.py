#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

from struct import *
from py_utilities import *

''' EEP - device profile of radio telegrams definition '''
class A5_10_03():
    "EEP: Room operating panel 0..40°C, temperature sensor, set point control"

    def __init__(self):
        self.setPoint = 0
        self.temperature = 0
        self.modeDay = 0
        self.modeNight = 0

    def unpack(self, data, optData):
        #data[0] = RORG
        #data[1] = not used
        #data[2] = set point (0..100%)
        #data[3] = temperature (0x00..40°C, 0xff..0°C)
        #data[4] = keys
        self.setPoint = data[2] * 40 / 255      #proportional
        
        self.temperature = float(40)*(255-data[3])/float(255) #inverted proportional

        if (data[4] & 0x01 == 1):
            self.modeDay = 1
            self.modeNight = 0            
        else:
            self.modeDay = 0
            self.modeNight = 1            
            
            
    def pack(self, senderID = 'ffffff', destinationID = 'ffffff'):
        data = bytearray()
        optData = bytearray()
        
        print("Enocean: A5_10_03 profile pack not defined")
        return(data, optData)
