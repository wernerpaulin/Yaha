#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

from struct import *
from utilities.bits_and_bytes import *

''' EEP - device profile of radio telegrams definition '''
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
        self.anyRockerPressed = 0    #any key

    def unpack(self, data, optData):
        #data[0] = RORG
        #data[1] = User data: DB0.7...DB0.5
        rocker1stAction         = data[1] >> 5 & 0x07
        rockerPressed           = data[1] >> 4 & 0x01
        rocker2ndAction         = data[1] >> 1 & 0x07
        rocker2ndActionIsValid  = data[1] & 0x01
        
        #assign extracted data to variables
        self.anyRockerPressed = rockerPressed
        
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
            self.anyRockerPressed = 0

    def pack(self, senderID = 'ffffff', destinationID = 'ffffff', subTypeOptionString = None):
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
