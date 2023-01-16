#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

from struct import *
from py_utilities import *

''' EEP - device profile of radio telegrams definition '''
class A5_11_04():
    "EEP: Controller Status, Extended Lighting Status"
    PARAMETER_MODE_DIMMER_ONTIME = 0
    PARAMETER_MODE_RGB = 1
    PARAMETER_MODE_ENERGY = 2
    
    
    def __init__(self):
        self.energy = 0
        self.onTime = 0
        self.switchedOn = 0
        self.dimmValue = 0
        self.errorLamp = 0
        self.errorInternal = 0
        self.errorExternal = 0

    def unpack(self, data, optData):
        #output state
        self.switchedOn = data[4] & 0x01    

        #error state
        errorState = data[4] >> 4 & 0x03
        self.errorLamp = 0
        self.errorInternal = 0
        self.errorExternal = 0
        self.RGBred = 0
        self.RGBgreen = 0
        self.RGBblue = 0
        
        if errorState == 1:
            self.errorLamp = 1
        elif errorState == 2:
            self.errorInternal = 1
        elif errorState == 3:
            self.errorExternal = 1
        
        #check if data are live data, otherwise ignore this data
        if data[4] >> 3 & 0x01 <> 1:
            return
        
        onTimeAvailable = data[4] >> 6 & 0x01
        parameterMode = data[4] >> 1 & 0x03
        
        if parameterMode == self.PARAMETER_MODE_DIMMER_ONTIME:
            self.dimmValue = data[1]
            if (onTimeAvailable == 1):
                self.onTime = join2BytesToInt(data[2:4], 'big')
        elif parameterMode == self.PARAMETER_MODE_RGB:
            self.RGBred = data[1]
            self.RGBgreen =  data[2]
            self.RGBblue =  data[3]     
        elif parameterMode == self.PARAMETER_MODE_ENERGY:
            self.energy = join2BytesToInt(data[1:3], 'big')
            
    def pack(self, senderID = 'ffffff', destinationID = 'ffffff', subTypeOptionString = None):
        data = bytearray()
        optData = bytearray()

        print("Enocean: A5_11_04 profile pack not defined")
        return(data, optData)