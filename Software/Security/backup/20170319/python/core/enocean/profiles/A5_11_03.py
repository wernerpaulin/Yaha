#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

from struct import *
from utilities.bits_and_bytes import *

''' EEP - device profile of radio telegrams definition '''
class A5_11_03():
    "EEP: Controller Status, Blind Status"
    
    def __init__(self):
        self.statusStopped = 0
        self.statusOpening  = 0
        self.statusClosing = 0
        self.statusNoEndPos = 0
        self.statusFullyOpen = 0
        self.statusFullyClosed = 0
        self.errorNoEndPosCfg = 0
        self.errorInternal = 0
        self.currentPosition = 0
        self.currentAngle = 0

    def unpack(self, data, optData):
        #data[0] = RORG
        #data[1] = DB3
        #data[2] = DB2
        #data[3] = DB1
        #data[4] = DB0
        
        #check if data are live data, otherwise ignore this data
        if data[4] >> 3 & 0x01 != 1:
            return		
        
        #shutter state
        shutterState = data[3] & 0x03
        
        self.statusStopped = 0
        self.statusOpening  = 0
        self.statusClosing = 0
        if shutterState == 1:
        	self.statusStopped = 1
        elif shutterState == 2:
        	self.statusOpening = 1
        elif shutterState == 3:
        	self.statusClosing = 1
        
        #end position state
        endPosState = (data[3] >> 2) & 0x03
        self.statusNoEndPos = 0
        self.statusFullyOpen = 0
        self.statusFullyClosed = 0
        if endPosState == 1:
        	self.statusNoEndPos = 1
        elif endPosState == 2:
        	self.statusFullyOpen = 1
        elif endPosState == 3:
        	self.statusFullyClosed = 1
        
        #error state
        errorState = (data[3] >> 4) & 0x03
        self.errorNoEndPosCfg = 0
        self.errorInternal = 0
        if errorState == 1:
        	self.errorNoEndPosCfg = 1
        elif errorState == 2:
        	self.errorInternal = 1
        
        #get angle position if available
        if (data[3] >> 6 & 0x01) == 1:
            self.currentAngle = (data[2] & 0x7F) * 2			#value angle is given in 2° steps
            if (data[3] >> 7 & 0x01) == 1:						#sign
                self.currentAngle = self.currentAngle * (-1)
        else:
        	self.currentAngle = 0
        	
        #get shutter position if available
        if (data[3] >> 7 & 0x01) == 1:
            self.currentPosition = data[1]                      #value	0..100%
        else:
        	self.currentPosition = 0

            
    def pack(self, senderID = 'ffffff', destinationID = 'ffffff', subTypeOptionString = None):
        data = bytearray()
        optData = bytearray()

        print("Enocean: A5_11_03 profile pack not defined")
        return(data, optData)