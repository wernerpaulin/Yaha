#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/enocean.py
#python /home/pi/Yaha/yaha_main.py

from struct import *

from profiles.F6_02_01 import * 
from profiles.A5_11_03 import * 
from profiles.A5_11_04 import * 
from profiles.A5_10_03 import * 
from profiles.A5_38_08 import * 


class PacketTypeRadio():
    "Supported Enocean Equipment Profiles of radio telegrams"
    #Radio message types
    RORG_RPS = 0xF6
    RORG_1BS = 0xD5
    RORG_4BS = 0xA5
    RORG_VLD = 0xD2
    
    def __init__(self):
        self.F6_02_01 = F6_02_01()
        self.A5_11_03 = A5_11_03()
        self.A5_11_04 = A5_11_04()
        self.A5_10_03 = A5_10_03()
        self.A5_38_08 = A5_38_08()

        self.supportedProfiles = supportedProfiles()
        self.ownID = None
        self.hostChannel = None
        self.hostID = None
        self.type = None
        self.subType = None
        self.subTypeUnpack = None
        self.subTypePack = None
        self.txDataList = list()

    def setSupportedInputProfile(self, type, subType):
       self.supportedProfiles.input[type] = subType  

    def setSupportedOutputProfile(self, type, subType):
       self.supportedProfiles.output[type] = subType  

    def unpack(self, data, optData):
        try:
            self.type = ''.join(format(x, '02x') for x in data[0:1])          #get RORG type of radio packet (e.g. F6)  
            self.subType = getattr(self, self.supportedProfiles.input[self.type].upper())   #get access to implemented sub type class for RORG type (e.g. F6) in data (1. byte) (e.g. F6_02_01)
            self.subTypeUnpack = getattr(self.subType, 'unpack')              #get access to unpack-function of sub type
            self.subTypeUnpack(data, optData)                                 #execute unpack-function
        except:
            print('EEP type <%s> or sub type <%s> is not supported'%(self.type, self.subType))

            
    def pack(self, subType, subTypeOptionString):
        self.subTypePack = getattr(self.subType, 'pack')                      #get access to pack-function of sub type

        #build specific host ID for this device based on host ID + channel
        hostIDwithChannel = hex(int(self.hostID, 16) + self.hostChannel)[2:-1]

        try:
            txData, txOptData = self.subTypePack(hostIDwithChannel, self.ownID, subTypeOptionString)  #execute pack-function
            return(txData, txOptData)
        except Exception, self.e:
            print("EEP pack function returned no or invalid data: tag <%s>: %s" %(self.subTypePack, self.e))
            return(bytearray(),bytearray())
        
    def getTagValue(self, subType, tag):
        try:
            self.subType = getattr(self, subType)                           #get access to sub type class in EEP (e.g. F6_02_01)
            self.subTypeTag = getattr(self.subType, tag)                    #get access to a specific tag holding variable values
            return(self.subTypeTag)
        except Exception, self.e:
            print('EEP get: tag <%s> does not exist in sub type <%s>: %s'%(tag, subType, self.e))
            return
        
    def setTagValue(self, subType, tag, subTypeOptionString, value):
        txData = bytearray()
        txOptData = bytearray()
        
        try:
            self.subType = getattr(self, subType)                           #get access to sub type class in EEP (e.g. F6_02_01)
            getattr(self.subType, tag)                                      #try to access this attribute to avoid creating an attribute with setattr just because someone misspelled a name: try will indicate an error
            setattr(self.subType, tag, value)                               #write value to tag variable (sent with next frame to device)
    
            txData, txOptData = self.pack(subType, subTypeOptionString)     #generic pack function: packs all data of a certain sub type: as external information only source and destination ID ncessary
            self.txDataList.append([txData, txOptData])
            return
        except Exception, self.e:
            print('EEP get: tag <%s> does not exist in sub type <%s>: %s'%(tag, subType, self.e))
            return
    
    def isReady(self):
        if self.hostID == None:
            return(0)
        else:
            return(1)
        
class supportedProfiles():
    def __init__(self):
        self.input = dict()           
        self.output = dict()