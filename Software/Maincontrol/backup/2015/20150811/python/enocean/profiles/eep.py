#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/enocean.py
#python /home/pi/Yaha/yaha_main.py

from struct import *
from py_utilities import *


''' EEP - device profile of radio telegrams definition / Begin '''
class F6_02_01():
    "EEP: Rocker Switch, 2 Rocker, Light and Blind Control - Application Style 1"
    '''
    Description:
    Device has max. 2 rockers: rockerA, rockerB
    Each rocker has 2 switch positions: rockerA0, rockerA1 / rockerB0, rockerB1 
    The profile supports also that both switch positions are pressed simultaneously
    '''
    def __init__(self):
        self.rockerA0 = 0
        self.rockerA1 = 0
        self.rockerB0 = 0
        self.rockerB1 = 0

    def unpack(self, data, optData):
        #data[0] = RORG
        #data[1] = User data: DB0.7...DB0.5
        rocker1stAction         = data[1] >> 5 & 0x07
        rockerPressed           = data[1] >> 4 & 0x01
        rocker2ndAction         = data[1] >> 1 & 0x07
        rocker2ndActionIsValid  = data[1] & 0x01
        
        #assign extracted data to variables
        if (rocker1stAction == 0):
            self.rockerA1 = rockerPressed
        elif (rocker1stAction == 1):
            self.rockerA0 = rockerPressed
        elif (rocker1stAction == 2):
            self.rockerB1 = rockerPressed
        elif (rocker1stAction == 3):
            self.rockerB0 = rockerPressed
            
        #if 2nd action is valid another button has been pressed simultaneously 
        if (rocker2ndActionIsValid == 1):
            if (rocker2ndAction == 0):
                self.rockerA1 = rockerPressed
            elif (rocker2ndAction == 1):
                self.rockerA0 = rockerPressed
            elif (rocker2ndAction == 2):
                self.rockerB1 = rockerPressed
            elif (rocker2ndAction == 3):
                self.rockerB0 = rockerPressed            
                
        #if no rocker bits are set reset all variables
        if ((data[1] >> 4 & 0x0F) == 0x00):
            self.rockerA0 = 0
            self.rockerA1 = 0
            self.rockerB0 = 0
            self.rockerB1 = 0            

    def pack(self, senderID = 'ffffff', destinationID = 'ffffff'):
        data = bytearray()
        optData = bytearray()
        byte0 = 0
        byte1 = 0
        byte2 = 0
        byte3 = 0
        rockerPressed = 0
        rocker1stAction = 0
        rocker2ndAction = 0
        rocker2ndActionIsValid = 0
        

        #code rocker 1st action
        if self.rockerA1 == 1:
            rocker1stAction = 0
        elif self.rockerA0 == 1:
            rocker1stAction = 1
        elif self.rockerB1 == 1:
            rocker1stAction = 2
        elif self.rockerB0 == 1:
            rocker1stAction = 3

        rockerPressed   = int(bool(self.rockerA0) | bool(self.rockerA1) | bool(self.rockerB0) | bool(self.rockerB1))
        rockerPressed   = rockerPressed   << 4 & 0x10       #Bit 4
        rocker1stAction = rocker1stAction << 5 & 0xE0       #Bit 7...5
        
        #rocker 2nd action not implemented because priority of buttons is not clear
        rocker2ndAction         = 0
        rocker2ndActionIsValid  = 0
        
        #build data
        #[0]: RORG
        data.append(0xF6)       
        #[1]: data
        data.append(rocker1stAction | rockerPressed | rocker2ndAction | rocker2ndActionIsValid)
        #[2..5]: sender ID
        byte3, byte2, byte1, byte0 = splitLongIn4Bytes(int(senderID, 16), 'big')
        data.append(byte3)       
        data.append(byte2)       
        data.append(byte1)       
        data.append(byte0)       
        #[6]: status
        data.append(rockerPressed | 0x20)  #PEHA special: set T21-bit (0x20) of status byte otherwise teaching is not working on Peha relays?!
        
        #build optional data
        #[0]: sub telegram
        optData.append(0x01)       
        #[1..4]: destination ID
        destinationID = 'ffffffff'      #PEHA special: override destination ID as Peha devices would not accept specifically addressed packets 
        byte3, byte2, byte1, byte0 = splitLongIn4Bytes(int(destinationID, 16), 'big')
        optData.append(byte3)       
        optData.append(byte2)       
        optData.append(byte1)       
        optData.append(byte0)       
        #[5]: dbm 
        optData.append(0x3c) 
        #[6]: Security level
        optData.append(0x00) 
        
        return(data, optData)

class A5_11_04():
    "EEP: Controller Status, Extended Lighting Status"
    def __init__(self):
        self.energy = 0
        self.operatingHours = 0

    def unpack(self, data, optData):
        print("TODO: A5_11_04 unpack")
        pass

    def pack(self, senderID = 'ffffff', destinationID = 'ffffff'):
        print("TODO: A5_11_04 pack")
        pass

class PacketTypeRadio():
    "Supported Enocean Equipment Profiles of radio telegrams"
    #Radio message types
    RORG_RPS = 0xF6
    RORG_1BS = 0xD5
    RORG_4BS = 0xA5
    RORG_VLD = 0xD2
    
    def __init__(self):
        self.supportedProfiles = dict()
        self.hostID = None
        self.ownID = None
        self.F6_02_01 = F6_02_01()
        self.A5_11_04 = A5_11_04()
        self.type = None
        self.subType = None
        self.subTypeUnpack = None
        self.subTypePack = None
        self.txDataList = list()

    def setSupportedProfile(self, type, subType):
       self.supportedProfiles[type] = subType  
       print(self.supportedProfiles[type])

    def unpack(self, data, optData):
        try:
            self.type = ''.join(format(x, '02x') for x in data[0:1])          #get RORG type of radio packet (e.g. F6)  
            self.subType = getattr(self, self.supportedProfiles[self.type])   #get access to implemented sub type class for RORG type (e.g. F6) in data (1. byte) (e.g. F6_02_01)
            self.subTypeUnpack = getattr(self.subType, 'unpack')              #get access to unpack-function of sub type
            self.subTypeUnpack(data, optData)                                 #execute unpack-function
        except:
            print('EEP type <%s> or sub type <%s> is not supported'%(self.type, self.subType))

            
    def pack(self, subType):
        self.subTypePack = getattr(self.subType, 'pack')                      #get access to pack-function of sub type
        txData, txOptData = self.subTypePack(self.hostID, self.ownID)         #execute unpack-function
        return(txData, txOptData)
        
    def getTagValue(self, subType, tag):
        try:
            self.subType = getattr(self, subType)                           #get access to sub type class in EEP (e.g. F6_02_01)
            self.subTypeTag = getattr(self.subType, tag)                    #get access to a specific tag holding variable values
            return(self.subTypeTag)
        except:
            print('EEP tag <%s> does not exist in sub type <%s>'%(tag, subType))
            return
        
    def setTagValue(self, subType, tag, value):
        txData = bytearray()
        txOptData = bytearray()
        
        try:
            self.subType = getattr(self, subType)                           #get access to sub type class in EEP (e.g. F6_02_01)
            getattr(self.subType, tag)                                      #try to access this attribute to avoid creating an attribute with setattr just because someone misspelled a name 
            setattr(self.subType, tag, value)                               #write value to tag variable (sent with next frame to device)
    
            txData, txOptData = self.pack(subType)                  #generic pack function: packs all data of a certain sub type: as external information only source and destination ID ncessary
            self.txDataList.append([txData, txOptData])
            return
        except:
            print('EEP tag <%s> does not exist in sub type <%s>'%(tag, subType))
            return

    
    
''' EEP - device profile of radio telegrams definition / End '''