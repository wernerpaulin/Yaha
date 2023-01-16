#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/core/ABE/driver.py
#python /home/pi/Yaha/yaha_main.py

import threading
import time

from ABE_ADCDifferentialPi import ADCDifferentialPi
from ABE_helpers import ABEHelpers


ABE_ADDRESS_ADC1 = 0x68         #i2c address of ADC 1
ABE_ADDRESS_ADC2 = 0x69         #i2c address of ADC 2
ABE_SAMPLING_RATE = 12          #12 bit = 4.5ms sampling time, 18 bit = 240ms sampling time!!!
ABE_UDC = 3.3                   #Use this voltage pins instead of 5V as it is very stable. The MCP3424 has an internal reference voltage of 2.048V = max. voltage: resistor sizing
ABE_i2c_ACCESS_WAIT_TIME = 0.2  #seconds until next read starts

class main():
    "Specific IO handler for ABE analog IOs"
    def __init__(self, PDI):
        self.ABE_TYPE_INDEX = 0
        self.DIRECTION_INDEX = 1
        self.CHANNEL_INDEX = 2
        self.OPTION_STRING_INDEX = 3
        
        self.PDI = PDI
        
        self.ioTags = dict()
        self.idStringElements = list() 
        self.readTags = dict()
        self.writeTags = dict()
        self.readIndex = 0
        
        self.adcInterface = None
        self.adcReadThreadHandle = None
        self.i2c_helper = None
        self.bus = None
        
        self.i2cStartTime = None
        
        #get all PDI tags where ABE is specified as owner => all these tags will be handled by the ABE driver
        self.ioTags = PDI.getTagDeviceIDs('ABE')  #"tag" : ID
        for tag in self.ioTags:
            try:
                #device IDs are formated like: ADCDiff.IN.1.r:10000
                idStringElements = self.ioTags[tag].split(".")
                #populate read and write list with object which should be handled by the driver
                if idStringElements[self.DIRECTION_INDEX].lower() == "in":
                    self.readTags[tag] = ioPoint()
                    self.readTags[tag].processTag = tag

                    self.readTags[tag].ABEtype      = idStringElements[self.ABE_TYPE_INDEX]
                    self.readTags[tag].direction    = idStringElements[self.DIRECTION_INDEX]
                    self.readTags[tag].channel      = int(idStringElements[self.CHANNEL_INDEX])
                    try:
                        self.readTags[tag].optionString = idStringElements[self.OPTION_STRING_INDEX]
                    except:
                        self.readTags[tag].optionString = None
                else:
                    print("IO: ABE ADC board has no output channels. Tag: {0}".format(tag))
                    self.writeTags[tag] = ioPoint()
                    self.writeTags[tag].processTag = tag

                    self.writeTags[tag].ABEtype      = idStringElements[self.ABE_TYPE_INDEX]
                    self.writeTags[tag].direction    = idStringElements[self.DIRECTION_INDEX]
                    self.writeTags[tag].channel      = int(idStringElements[self.CHANNEL_INDEX])
                    try:
                        self.writeTags[tag].optionString = idStringElements[self.OPTION_STRING_INDEX]
                    except:
                        self.writeTags[tag].optionString = None

            except Exception, self.e:
                print "IO: error in PDI owner ID for ABE: " + str(self.e)            

        #start driver only if PDI tags are configured for ABE
        if (len(self.ioTags) > 0):
            self.start()

    def start(self):
        try:
            self.i2c_helper = ABEHelpers()
            self.bus = self.i2c_helper.get_smbus()            
            
            self.adcInterface = ADCDifferentialPi(self.bus, ABE_ADDRESS_ADC1, ABE_ADDRESS_ADC2, ABE_SAMPLING_RATE)
            self.adcInterface.set_conversion_mode(0)
    
            self.adcReadThreadHandle = threading.Thread(target=self.adcReadThread)
            self.adcReadThreadHandle.start()
        
        except Exception, self.e:
            print "ABE IO: error initializing i2c: {0}".format(self.e)            

    def adcReadThread(self):
        self.readIndex = 0
        while (True):
            #read voltage of all channels configured

            #read only one value per cycle to avoid cycle time violations due to synchrnonous i2c access in python
            tag = self.readTags.keys()[self.readIndex]
            self.i2cStartTime = time.time()
            #One access to i2c bus takes around 240ms!!!
            self.readTags[tag].adcVoltage = self.adcInterface.read_voltage(self.readTags[tag].channel)
            
            #if (self.readTags[tag].channel == 1):
            #    print("Tag {0}: {1}V - channel: {2}".format(tag, self.readTags[tag].adcVoltage,self.readTags[tag].channel))
            
            #after sleep: read next tag
            self.readIndex = self.readIndex + 1
            if (self.readIndex >= len(self.readTags)):
                self.readIndex = 0 
            
            # wait 0.5 seconds before reading the pins again
            time.sleep(ABE_i2c_ACCESS_WAIT_TIME)  
        

    def readInputs(self):
        #go through all tags which should be read from io driver and write current value directly into PDI
        #io driver reads a voltage which will be converted to resistance if voltage divider is specified
        for tag in self.readTags:
            #do not interpret voltage if not yet read the first time
            if (self.readTags[tag].adcVoltage == None):
                continue
            
            if (self.readTags[tag].optionString != None):
                #optionString = r:10000
                try:
                    r1 = float(self.readTags[tag].optionString.split(":")[1])  #contains pull-up resistance in Ohm
                    r2 = (self.readTags[tag].adcVoltage * r1) / (ABE_UDC - self.readTags[tag].adcVoltage)
                except:
                    r2 = 0
                    
                setattr(self.PDI, self.readTags[tag].processTag, r2)
            else:
                #no option string defined -> take directly adc voltage
                setattr(self.PDI, self.readTags[tag].processTag, self.readTags[tag].adcVoltage)
    
    def writeOutputs(self):
        #ABE ADC board has not output channels
        pass
        

class ioPoint():
    "Representation of a single IO point e.g. ADCDiff.IN.1.r:10000"    
    def __init__(self):
        self.ABEtype = None
        self.direction = None
        self.channel = None
        self.optionString = None
        self.processTag = None
        self.processTagOldValue = None
        self.adcVoltage = None
