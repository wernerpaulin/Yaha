#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py
#python /home/pi/Yaha/yaha_enocean.py

import serial
import fcntl, socket
import time
import py_utilities
from struct import *

# EnOceanSerialProtocol3.pdf / 12
class ESP3_PACKET():
    RESERVED = 0x00
    RADIO = 0x01
    RESPONSE = 0x02
    RADIO_SUB_TEL = 0x03
    EVENT = 0x04
    COMMON_COMMAND = 0x05
    SMART_ACK_COMMAND = 0x06
    REMOTE_MAN_COMMAND = 0x07
    RADIO_MESSAGE = 0x09
    RADIO_ADVANCED = 0x0A
    
    

class ESP3_TGM():
    SYNC_BYTE = 0x55
    SYNC_BYTE_INDEX = 0
    DATA_LENGTH_INDEX = 1
    OPT_DATA_LENGTH_INDEX = 3
    DATA_START_INDEX = 6
    PACKET_TYPE_INDEX = 4
    CRC_HEADER_INDEX = 5

class ESP3_RORG():
    RPS = 0xF6
    FOUR_BS = 0xA5
    VLD = 0xD2 

esp3_tgm = ESP3_TGM()
esp3_packet = ESP3_PACKET()

class ESP3_RORG_F6():
    def getSenderID(self, tgm):
        return tgm[esp3_tgm.DATA_START_INDEX + 2:DATA_START_INDEX+2+4]
    
esp3_rorg_f6 = ESP3_RORG_F6()




class Driver:
    'Yaha EnOcean driver: communicates with Enocean devices'
    def __init__(self):
        self.statemachine = {
                             "sIdle": self.sIdle,
                             "sWait1": self.sWait1,
                             "sWait2": self.sWait2,
                             "sSwitch1Press": self.sSwitch1Press,
                             "sSwitch1Release": self.sSwitch1Release,
                             "sSwitch2Press": self.sSwitch2Press,
                             "sSwitch2Release": self.sSwitch2Release
                            }
        self.activeState = "sSwitch1Press"
        self.activeStateOld = ""

        #set enocean sender ID to first 4 digits of mac address 
        self.senderID = py_utilities.getHwAddr('eth0')
        self.senderID = self.senderID.split(":")
        self.senderID = self.senderID[0:4]
        self.senderID = ''.join(self.senderID)  #join byte list to a string

        self.logEnocean = ""
        self.rxFrame = ""
        self.txFrame = ""
        self.txFrameData = [0 for x in range(21)]

        

        # configure the serial connections (the parameters differs on the device you are connecting to)
        self.serIf = serial.Serial(
            port='/dev/ttyAMA0',
            baudrate=57600,
            parity=serial.PARITY_NONE,
            timeout = 0.1,
            interCharTimeout = 0.1,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

        #open serial port
        try: 
            self.serIf.open()
        except Exception, self.e:
            print "Error open serial port: " + str(self.e)

        #flush current buffer
        if self.serIf.isOpen():
            try:
                self.serIf.flushInput() #flush input buffer, discarding all its contents
                self.serIf.flushOutput()#flush output buffer, aborting current output 
            except Exception, self.e1:
                print "error communicating...: " + str(self.e1)
                self.serIf.close()
        else:
            print "Cannot open serial port"

    def processRxTgm(self):
        #skip rx processing if rx-buffer is empty
        if self.serIf.inWaiting() == 0:
            return
        
        # read all characters in buffer
        self.rxTgm = bytearray(self.serIf.read(self.serIf.inWaiting()))
        print("RX: " + ''.join(format(x, '02x') for x in self.rxTgm))
        self.logEnocean += ''.join(format(x, '02x') for x in self.rxTgm) + "\r\n" 

        
        #Check whether frame starts with sync byte
        if (self.rxTgm[esp3_tgm.SYNC_BYTE_INDEX] != esp3_tgm.SYNC_BYTE):
            self.serIf.flushInput()
            print("Enocean: Rx: missing sync byte")
            return
        
        #Check CRC of header
        if (py_utilities.checkCRC8correct(self.rxTgm[esp3_tgm.SYNC_BYTE_INDEX+1:esp3_tgm.CRC_HEADER_INDEX],self.rxTgm[esp3_tgm.CRC_HEADER_INDEX]) == False):
            self.serIf.flushInput()
            print('Enocean: Rx: CRC of header incorrect')
            return

        #Calculate length of data and optional data
        self.rxTgmDataLength = py_utilities.join2BytesToInt(self.rxTgm[esp3_tgm.DATA_LENGTH_INDEX:esp3_tgm.DATA_LENGTH_INDEX+2], 'big')
        self.rxTgmOptDataLength = self.rxTgm[esp3_tgm.OPT_DATA_LENGTH_INDEX]
        
        #Check CRC of data
        self.dataStartIndex = esp3_tgm.DATA_START_INDEX
        self.dataEndIndex = self.dataStartIndex + self.rxTgmDataLength + self.rxTgmOptDataLength

        try:
            if (py_utilities.checkCRC8correct(self.rxTgm[self.dataStartIndex:self.dataEndIndex],self.rxTgm[self.dataEndIndex]) == False):
                self.serIf.flushInput()
                print('Enocean: Rx: CRC of data incorrect')
                return
        except:
            print('Enocean: Rx: CRC position calculation failed')
            return
            

        #Header and data are valid: further processing according to packet type and R-ORG
        if (self.rxTgm[esp3_tgm.PACKET_TYPE_INDEX] != esp3_packet.RADIO):
            print('Enocean: Rx: packet type not supported: %s'%(self.rxTgm[esp3_tgm.PACKET_TYPE_INDEX]))
            return
        
        '''weiter machen: Klassen für RORG anlegen und mittels dict auf getSenderID verweisen'''
        '''je nach Sender ID: Zugriff auf XML und alle eingehängten Funktionen abarbeiten und Daten extrahieren'''
        '''Im zyklischen Teil über alle Enocean Variablen loopen und Werte mittels Get-Funktion von Enocean abholen'''
        '''ACHTUNG: in einem Empfang-Tgm könnten auch mehrere Telegramme enthalten sein: prüfen der Länge und vereinzeln'''
  
           
    def sIdle(self):
        self.activeState = "sIdle"
        return
        
    def sSwitch1Press(self):
        self.activeState = "sWait1"
        
        length = 7
        optLength = 7
        
        self.txFrameData[0] = esp3_tgm.SYNC_BYTE
        self.txFrameData[1], self.txFrameData[2] = py_utilities.splitIntIn2Bytes(length, "big")
        self.txFrameData[3] = optLength
        self.txFrameData[4] = esp3_packet.RADIO
        self.txFrameData[5] = py_utilities.calcCRC8sum(self.txFrameData[1:5])
        self.txFrameData[6] = ESP3_RORG.RPS
        self.txFrameData[7] = 0x70
        self.txFrameData[8], self.txFrameData[9], self.txFrameData[10], self.txFrameData[11] = py_utilities.splitLongIn4Bytes(int(self.senderID, 16), "big")
        self.txFrameData[12] = 0x30
        self.txFrameData[13] = 0x01
        self.txFrameData[14], self.txFrameData[15], self.txFrameData[16], self.txFrameData[17] = 0xFF, 0xFF, 0xFF, 0xFF
        self.txFrameData[18] = 0x37
        self.txFrameData[19] = 0x00
        self.txFrameData[20] = py_utilities.calcCRC8sum(self.txFrameData[6:-1])
        
        self.serIf.write(bytearray(self.txFrameData))

        self.startTime = time.time()
        return

    def sWait1(self):
        if (time.time() >= self.startTime + 2.0):
            self.activeState = "sSwitch1Release"
        
        return

    def sSwitch1Release(self):
        self.txFrameData[7] = 0x00
        self.txFrameData[12] = 0x20
        self.txFrameData[20] = py_utilities.calcCRC8sum(self.txFrameData[6:-1])
        

        self.serIf.write(bytearray(self.txFrameData))

        self.activeState = "sSwitch2Press"
        return

    def sSwitch2Press(self):
        self.activeState = "sWait2"
        self.txFrameData[7] = 0x50
        self.txFrameData[12] = 0x30
        self.txFrameData[20] = py_utilities.calcCRC8sum(self.txFrameData[6:-1])

    def sWait2(self):
        if (time.time() >= self.startTime + 2.0):
            self.activeState = "sSwitch2Release"
        
        return

    def sSwitch2Release(self):
        self.txFrameData[7] = 0x00
        self.txFrameData[12] = 0x20
        self.txFrameData[20] = py_utilities.calcCRC8sum(self.txFrameData[6:-1])
        

        self.serIf.write(bytearray(self.txFrameData))

        self.activeState = "sIdle"
        return
        

    def update(self):
        self.statemachine[self.activeState]()
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Enocean state: " + self.activeState)
        
        #check receive buffer every update cycle
        self.processRxTgm()

