#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/enocean.py
#python /home/pi/Yaha/yaha_main.py

from struct import *
from py_utilities import *
from profiles.F6_02_01 import * 
from profiles.A5_11_04 import * 
from profiles.A5_10_03 import * 


class PacketTypeRadio():
    "Supported Enocean Equipment Profiles of radio telegrams"
    #Radio message types
    RORG_RPS = 0xF6
    RORG_1BS = 0xD5
    RORG_4BS = 0xA5
    RORG_VLD = 0xD2
    
    def __init__(self):
        self.F6_02_01 = F6_02_01()
        self.A5_11_04 = A5_11_04()
        self.A5_10_03 = A5_10_03()

        self.supportedProfiles = dict()
        self.hostID = None
        self.ownID = None
        self.type = None
        self.subType = None
        self.subTypeUnpack = None
        self.subTypePack = None
        self.txDataList = list()

    def setSupportedProfile(self, type, subType):
       self.supportedProfiles[type] = subType  
       #print(self.supportedProfiles[type])

    def unpack(self, data, optData):
        try:
            self.type = ''.join(format(x, '02x') for x in data[0:1])          #get RORG type of radio packet (e.g. F6)  
            self.subType = getattr(self, self.supportedProfiles[self.type].upper())   #get access to implemented sub type class for RORG type (e.g. F6) in data (1. byte) (e.g. F6_02_01)
            self.subTypeUnpack = getattr(self.subType, 'unpack')              #get access to unpack-function of sub type
            self.subTypeUnpack(data, optData)                                 #execute unpack-function
        except:
            print('EEP type <%s> or sub type <%s> is not supported'%(self.type, self.subType))

            
    def pack(self, subType):
        self.subTypePack = getattr(self.subType, 'pack')                      #get access to pack-function of sub type
        try:
            txData, txOptData = self.subTypePack(self.hostID, self.ownID)         #execute unpack-function
            return(txData, txOptData)
        except Exception, self.e:
            print("EEP pack function returned no or invalid data: tag <%s>" %(self.subTypePack))
            return(bytearray(),bytearray())
        
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
            getattr(self.subType, tag)                                      #try to access this attribute to avoid creating an attribute with setattr just because someone misspelled a name: try will indicate an error
            setattr(self.subType, tag, value)                               #write value to tag variable (sent with next frame to device)
    
            txData, txOptData = self.pack(subType)                  #generic pack function: packs all data of a certain sub type: as external information only source and destination ID ncessary
            self.txDataList.append([txData, txOptData])
            return
        except:
            print('EEP tag <%s> does not exist in sub type <%s>'%(tag, subType))
            return
        