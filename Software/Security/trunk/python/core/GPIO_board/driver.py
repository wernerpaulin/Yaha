#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/core/ABE/driver.py
#python3 /home/pi/Yaha/yaha_main.py

#import RPi.GPIO as GPIO
from RPi import GPIO

class main():
    "Specific IO handler for GPIOs"
    def __init__(self, PDI):
        self.GPIO_TYPE_INDEX = 0
        self.DIRECTION_INDEX = 1
        self.CHANNEL_INDEX = 2
        
        self.PDI = PDI
        
        self.ioTags = dict()
        self.idStringElements = list() 
        self.readTags = dict()
        self.writeTags = dict()
        self.readIndex = 0
        
        #get all PDI tags where ABE is specified as owner => all these tags will be handled by the ABE driver
        self.ioTags = PDI.getTagDeviceIDs('GPIO')  #"tag" : ID
        for tag in self.ioTags:
            try:
                #device IDs are formated like: ADCDiff.IN.1.r:10000
                idStringElements = self.ioTags[tag].split(".")
                #populate read and write list with object which should be handled by the driver
                if idStringElements[self.DIRECTION_INDEX].lower() == "in":
                    self.readTags[tag] = ioPoint()
                    self.readTags[tag].processTag = tag

                    self.readTags[tag].GPIOtype  = idStringElements[self.GPIO_TYPE_INDEX]
                    self.readTags[tag].direction = idStringElements[self.DIRECTION_INDEX]
                    self.readTags[tag].channel   = idStringElements[self.CHANNEL_INDEX]

                else:
                    self.writeTags[tag] = ioPoint()
                    self.writeTags[tag].processTag = tag

                    self.writeTags[tag].GPIOtype  = idStringElements[self.GPIO_TYPE_INDEX]
                    self.writeTags[tag].direction = idStringElements[self.DIRECTION_INDEX]
                    self.writeTags[tag].channel   = idStringElements[self.CHANNEL_INDEX]

            except Exception as e:
                print("IO: error in PDI owner ID for GPIO: {0}".format(e))            

        #start driver only if PDI tags are configured for GPIO
        if (len(self.ioTags) > 0):
            self.start()

    def start(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        #configure GPIO for inputs
        for tag in self.readTags:
            GPIO.setup(int(self.readTags[tag].channel), GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
        
        for tag in self.writeTags:
            GPIO.setup(int(self.writeTags[tag].channel), GPIO.OUT)
        

    def readInputs(self):
        #go through all tags which should be read from io driver and write current value directly into PDI
        for tag in self.readTags:
            setattr(self.PDI, self.readTags[tag].processTag, GPIO.input(int(self.readTags[tag].channel)))
    
    def writeOutputs(self):
        #go through all write tags and see if it has been changed since last write
        for tag in self.writeTags:
            #get current value from PDI
            currentValue = getattr(self.PDI, self.writeTags[tag].processTag)
            #see if it has been changed since last write to enocean module
            if currentValue != self.writeTags[tag].processTagOldValue:
                GPIO.output( int(self.writeTags[tag].channel), int(currentValue) )
                self.writeTags[tag].processTagOldValue = currentValue

class ioPoint():
    "Representation of a single IO point e.g. GPIO.IN.1"    
    def __init__(self):
        self.GPIOtype = None
        self.direction = None
        self.channel = None
        self.processTag = None
        self.processTagOldValue = None
