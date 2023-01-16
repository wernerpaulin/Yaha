#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

from struct import *
from utilities.bits_and_bytes import *
import json

''' EEP - device profile of radio telegrams definition '''
class A5_38_08():
    "EEP: Central Command, Gateway: Communication between gateway and actuators uses byte DB_3 to identify commands"
    '''
    Description: depending on the command type a various of actuators (blinds, switches,...) can be manipulated after being thought-in.
    '''
    CMD_SWITCHING = 0x01
    
    def __init__(self):
        self.time = 0           #1..65535 in 0.1s steps
        self.learning = 0
        self.unlockLock = 0     #if 1 actuator will not accept further commands until self.time is elapsed. if 0 bit has been set to 0 for unlock
        self.durationDelay = 0  #if 1 time will be interpreted as press duration of button
        self.switchOffOn = 0    #0: off, 1: on

    def unpack(self, data, optData):
        print("Enocean: A5_38_08 unpack not defined: data: " + ''.join(format(x, ' 02x') for x in data))


    def pack(self, senderID = 'ffffff', destinationID = 'ffffff', subTypeOptionString = None):
        byte0 = 0
        byte1 = 0
        byte2 = 0
        byte3 = 0
        
        data = bytearray()
        optData = bytearray()
        
        #build data
        #RORG
        data.append(0xA5)       
        
        #build data bytes (special tgm data in case of teach-in)
        if (self.learning == 1):
            self.learning = 0       #avoid multiple learning telegrams
            data.extend(self.buildTeachInData())
        else:
            data.extend(self.buildOperationalData(subTypeOptionString))
        
        #[5..8]: sender ID
        byte3, byte2, byte1, byte0 = splitLongIn4Bytes(int(senderID, 16), 'big')
        data.append(byte3)       
        data.append(byte2)       
        data.append(byte1)       
        data.append(byte0)       
        #[6]: status
        data.append(0x00)  #Repeater counter Bit3..Bit0
 
        #no optional data
        
        return(data, optData)
    
    def buildTeachInData(self):
        byte0 = 0
        byte1 = 0
        byte2 = 0
        byte3 = 0
        dataBytes = bytearray()
        eepFunc = 0x38
        eepTyp = 0x08
        manufacturerID = 0x7ff #MULTI_USER_MANUFACTURER = 0x7FF (https://www.enocean.com/fileadmin/redaktion/support/enocean-link/eo_manufacturer_8h.html)
        manIDhigh, manIDlow = splitIntIn2Bytes(manufacturerID, 'big')
        
        #build DB3
        byte3 = eepFunc << 2
        byte2 = (eepTyp >> 5) & 0x03        #we need the upper 2 bits to be merged with byte3
        byte3 = byte3 | byte2
        dataBytes.append(byte3)             #DB3
        
        #build DB2
        byte2 = (eepTyp << 3) & 0xf8        #we need lower 5 bytes which will be the upper 5 bits of DB2
        byte2 = byte2 | (manIDhigh & 0x07)  #only the first 3 bits of high byte are used          
        dataBytes.append(byte2)             #DB2

        #build DB1
        byte1 = manIDlow
        dataBytes.append(byte1)             #DB1
        
        
        #build DB0
        byte0 = byte0 | 0x80                #bit7... learn type (with EEP number and manuf. ID, bit3...teach-in tgm
        dataBytes.append(byte0)             #DB0
        
        return(dataBytes)

    
    def buildOperationalData(self, subTypeOptionString):
        byte0 = 0
        byte1 = 0
        byte2 = 0
        byte3 = 0
        dataBytes = bytearray()
        subTypeOptionDict = {'empty': 0}    #force creating a dictionary
        subTypeOptionDict.clear()           #clear dictionary immediately
        commandType = None

        #function type "A5_38_08" supports different command types. This is defined with the option string: cmd:0x01
        subTypeOptionDict = optionStringToDict(subTypeOptionString)
        try:
            commandType = int(subTypeOptionDict['cmd'], 16) #command type is in hex: 0x01
        except:
            pass
        
        #prepare data according to the command types
        if (commandType == self.CMD_SWITCHING):
            #DB3.7-3.0
            dataBytes.append(commandType)
    
            #DB2.7-1.0
            byte1, byte0 = splitIntIn2Bytes(self.time, 'big')
            dataBytes.append(byte1)
            dataBytes.append(byte0)
    
            #DB0: bit coded
            byte1, byte0 = splitIntIn2Bytes(int(1), 'big')
            byte3 = (byte0 & 0x01) << 3
    
            byte1, byte0 = splitIntIn2Bytes(int(self.unlockLock), 'big')
            byte3 = byte3 | (byte0 & 0x01) << 2
            
            byte1, byte0 = splitIntIn2Bytes(int(self.durationDelay), 'big')
            byte3 = byte3 | (byte0 & 0x01) << 1
            
            byte1, byte0 = splitIntIn2Bytes(int(self.switchOffOn), 'big')
            byte3 = byte3 | (byte0 & 0x01)
            
            byte3 = byte3 & 0x0F        #upper 4bits are not used
    
            dataBytes.append(byte3)
        
        else:
            print('A5_38_08 - unknown command type: %s'%(commandType))
            dataBytes.clear() 
        
            
        return(dataBytes)
        
def optionStringToDict(optionString):
    optionDict = {'empty': 0}    #force creating a dictionary
    optionDict.clear()           #clear dictionary immediately

    #option string format: cmd:0x01 , abx:read ,
    try:
        for options in optionString.split(','):
            key = options.strip().split(':')[0]         #cmd:0x01
            value = options.strip().split(':')[1]
            optionDict[key.strip()] = value.strip()
    except:
        pass

    return optionDict
