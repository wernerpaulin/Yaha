#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/enocean.py
#python /home/pi/Yaha/yaha_main.py

from struct import *
from py_utilities import *
import serial
import time
from profiles.eep import *

class ESP3:
    "Enocean Serial Protocoll 3 implementation"

    #ESP3 packet types
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
    
    
    #ESP3 packet structure
    SYNC_BYTE = 0x55
    SYNC_BYTE_INDEX = 0
    DATA_LENGTH_INDEX = 1
    OPT_DATA_LENGTH_INDEX = 3
    DATA_START_INDEX = 6
    PACKET_TYPE_INDEX = 4
    CRC_HEADER_INDEX = 5

    #ESP3 response return codes
    RET_OK = 0x00
    RET_NOT_SUPPORTED = 0x02
    RET_WRONG_PARAM = 0x03
    
    #TIMOUTS
    ESP3_PACKET_TIMEOUT = 0.1
    
    #ESP3 common command codes
    CO_RD_IDBASE = 0x08     #Function: Read ID range base number
    
    ENOCEAN_MAX_BASE_ID_CHANNELS = 128
    
        
    # https://gist.github.com/hypebeast/3833758
    crc8Table = (
        0x00, 0x07, 0x0e, 0x09, 0x1c, 0x1b, 0x12, 0x15, 0x38,
        0x3f, 0x36, 0x31, 0x24, 0x23, 0x2a, 0x2d, 0x70, 0x77,
        0x7e, 0x79, 0x6c, 0x6b, 0x62, 0x65, 0x48, 0x4f, 0x46,
        0x41, 0x54, 0x53, 0x5a, 0x5d, 0xe0, 0xe7, 0xee, 0xe9,
        0xfc, 0xfb, 0xf2, 0xf5, 0xd8, 0xdf, 0xd6, 0xd1, 0xc4,
        0xc3, 0xca, 0xcd, 0x90, 0x97, 0x9e, 0x99, 0x8c, 0x8b,
        0x82, 0x85, 0xa8, 0xaf, 0xa6, 0xa1, 0xb4, 0xb3, 0xba,
        0xbd, 0xc7, 0xc0, 0xc9, 0xce, 0xdb, 0xdc, 0xd5, 0xd2,
        0xff, 0xf8, 0xf1, 0xf6, 0xe3, 0xe4, 0xed, 0xea, 0xb7,
        0xb0, 0xb9, 0xbe, 0xab, 0xac, 0xa5, 0xa2, 0x8f, 0x88,
        0x81, 0x86, 0x93, 0x94, 0x9d, 0x9a, 0x27, 0x20, 0x29,
        0x2e, 0x3b, 0x3c, 0x35, 0x32, 0x1f, 0x18, 0x11, 0x16,
        0x03, 0x04, 0x0d, 0x0a, 0x57, 0x50, 0x59, 0x5e, 0x4b,
        0x4c, 0x45, 0x42, 0x6f, 0x68, 0x61, 0x66, 0x73, 0x74,
        0x7d, 0x7a, 0x89, 0x8e, 0x87, 0x80, 0x95, 0x92, 0x9b,
        0x9c, 0xb1, 0xb6, 0xbf, 0xb8, 0xad, 0xaa, 0xa3, 0xa4,
        0xf9, 0xfe, 0xf7, 0xf0, 0xe5, 0xe2, 0xeb, 0xec, 0xc1,
        0xc6, 0xcf, 0xc8, 0xdd, 0xda, 0xd3, 0xd4, 0x69, 0x6e,
        0x67, 0x60, 0x75, 0x72, 0x7b, 0x7c, 0x51, 0x56, 0x5f,
        0x58, 0x4d, 0x4a, 0x43, 0x44, 0x19, 0x1e, 0x17, 0x10,
        0x05, 0x02, 0x0b, 0x0c, 0x21, 0x26, 0x2f, 0x28, 0x3d,
        0x3a, 0x33, 0x34, 0x4e, 0x49, 0x40, 0x47, 0x52, 0x55,
        0x5c, 0x5b, 0x76, 0x71, 0x78, 0x7f, 0x6a, 0x6d, 0x64,
        0x63, 0x3e, 0x39, 0x30, 0x37, 0x22, 0x25, 0x2c, 0x2b,
        0x06, 0x01, 0x08, 0x0f, 0x1a, 0x1d, 0x14, 0x13, 0xae,
        0xa9, 0xa0, 0xa7, 0xb2, 0xb5, 0xbc, 0xbb, 0x96, 0x91,
        0x98, 0x9f, 0x8a, 0x8d, 0x84, 0x83, 0xde, 0xd9, 0xd0,
        0xd7, 0xc2, 0xc5, 0xcc, 0xcb, 0xe6, 0xe1, 0xe8, 0xef,
        0xfa, 0xfd, 0xf4, 0xf3)
    
    #calculate CRC check sum
    def calcCRC8sum(self,byteStream):
        crcSum = 0
        for c in byteStream:
            crcSum = self.crc8Table[crcSum & 0xFF ^ c & 0xFF]
        
        return crcSum

    def getPacketType(self, packet):
        try:
            return(packet[self.PACKET_TYPE_INDEX])
        except:
            return(0)
    
    def getDataLength(self, packet):
        try:
            return(join2BytesToInt(packet[self.DATA_LENGTH_INDEX:self.DATA_LENGTH_INDEX+2], 'big'))
        except:
            return(0)
    
    def getOptDataLength(self, packet):
        try:
            return(packet[self.OPT_DATA_LENGTH_INDEX])
        except:
            return(0)
    
    def extractDataBlock(self, packet):
        try:
            return(bytearray(packet[self.DATA_START_INDEX:self.DATA_START_INDEX + self.getDataLength(packet)]))
        except:
            return(0)

    def extractOptDataBlock(self, packet):
        try:
            return(bytearray(packet[self.DATA_START_INDEX + self.getDataLength(packet):self.DATA_START_INDEX + self.getDataLength(packet) + self.getOptDataLength(packet)]))
        except:
            return(0)


class ESP3_packet():
    def __init__(self):
        self.packetType = 0
        self.dataLength = 0
        self.optDataLength = 0
        self.data = bytearray()
        self.optData = bytearray()
        

class EnoceanDevice():
    "Enocean - each physical device is represented by this class"
    def __init__(self):
        self.packetTypeRadio = PacketTypeRadio()

class main():
    INVALID_HOST_ID = 0xffffffff
    
    "Enocean - manages serial communication and forwards frames for further processing to corresponding device"
    def __init__(self):
        self.esp3 = ESP3()
        self.deviceList = dict()                #this list contains all known devices referenced by their sender ID
        self.unknownDeviceList = dict()         #this list contains all devices from which telegrams have been received but not actions are implemented
        self.logEnocean = ""
        self.rxESP3packetList = list()
        self.rxBuffer = bytearray()
        self.txCommonComandList = list()
        self.hostID = self.INVALID_HOST_ID           #will be set dynamically

        self.txStatemachine = {
                             "sTxStateSend": self.sTxStateSend,
                             "sTxStateWait": self.sTxStateWait
                            }
        self.activeTxState = "sTxStateSend"
        self.activeTxStateOld = ""
        self.txWaitTimeStart = 0

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
            print "Enocean: error open serial port: " + str(self.e)

        #flush current buffer
        if self.serIf.isOpen():
            try:
                self.serIf.flushInput()     #flush input buffer, discarding all its contents
                self.serIf.flushOutput()    #flush output buffer, aborting current output 
            except Exception, self.e1:
                print "Enocean:  error communicating...: " + str(self.e1)
                self.serIf.close()
        else:
            print "Enocean: cannot open serial port"

        #get base ID of TCM310 enocean module
        self.txCommonComandList.append(0x08)

    def addDevice(self, deviceID='ffffffff', hostChannel=None):
        #create device
        deviceID = deviceID.lower()                 #ID is always considered lower case

        #add device only if not yet created        
        if not deviceID in self.deviceList:
            self.deviceList[deviceID] = EnoceanDevice()
            self.deviceList[deviceID].packetTypeRadio.ownID = deviceID
            
            if hostChannel <> None:
                if (int(hostChannel) <= self.esp3.ENOCEAN_MAX_BASE_ID_CHANNELS): 
                    self.deviceList[deviceID].packetTypeRadio.hostChannel = int(hostChannel)
                else:
                    self.deviceList[deviceID].packetTypeRadio.hostChannel = self.esp3.ENOCEAN_MAX_BASE_ID_CHANNELS
                    print("Enocean: host channel number is too high: %s (max: %s)"%(hostChannel, self.esp3.ENOCEAN_MAX_BASE_ID_CHANNELS))
            else:
                self.deviceList[deviceID].packetTypeRadio.hostChannel = 0
            
            #use saved host ID as back up just in case read base ID fails (this ID has to be once saved in PDI)
            self.deviceList[deviceID].packetTypeRadio.hostID = self.hostID

        return(self.deviceList[deviceID])

    def addDeviceFunctionType(self, deviceID='ffffffff', funcType=None):
        deviceID = deviceID.lower()                 #ID is always considered lower case
        funcType = funcType.lower() 

        #set specific profile which is supported by this device depending on the radio variant (RORG)
        if funcType.split("_")[0] == hex(self.deviceList[deviceID].packetTypeRadio.RORG_RPS)[2:]:   #F6_02_01 => F6
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_RPS)[2:], funcType)
        elif funcType.split("_")[0] == hex(self.deviceList[deviceID].packetTypeRadio.RORG_1BS)[2:]:
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_1BS)[2:], funcType)
        elif funcType.split("_")[0] == hex(self.deviceList[deviceID].packetTypeRadio.RORG_4BS)[2:]:
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_4BS)[2:], funcType)
        elif funcType.split("_")[0] == hex(self.deviceList[deviceID].packetTypeRadio.RORG_VLD)[2:]:
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_VLD)[2:], funcType)

    
    def unpackESP3packet(self):
        #go through all packages which have been received and CRC checked
        while len(self.rxESP3packetList) > 0:
            packet = self.rxESP3packetList.pop(0)   #get first telegram in list and remove it from list
            
            #Further processing depends on package type
            if (packet.type == self.esp3.RADIO):
                #get ID of sender: this 4-byte ID and a status byte are always the last 5 bytes of the data segment
                senderID = ''.join(format(x, '02x') for x in packet.data[len(packet.data)-5:len(packet.data)-1])
                senderID = senderID.lower()     #ID is always considered as lower case

                #call implemented enocean profile of this radio packet for this device (= sender)
                try:
                    self.deviceList[senderID].packetTypeRadio.unpack(packet.data, packet.optData)
                except:
                    self.unknownDeviceList[senderID] = ''.join(format(x, ' 02x') for x in packet.data)
                    print("Enocean: sender ID <%s> is unknown"%(senderID))
            elif (packet.type == self.esp3.RESPONSE):
                if len(packet.data) >= 1:
                    if packet.data[0] == self.esp3.RET_OK:
                        if len(packet.data) == 5:   #assume that a 5 byte response is linked to the read ID-Base common command (no other way to assume)
                            self.hostID = ''.join(hex(x)[2:] for x in packet.data[1:])  #build host ID from data byte 1-4
                            print("Enocean: Base ID successfully read: %s"%(self.hostID))
                            
                            #update all devices
                            for deviceID in self.deviceList: 
                                self.deviceList[deviceID].packetTypeRadio.hostID = self.hostID
                    else:
                        print("Enocean: Response received with return code %s"%(packet.data[0]))
                
            else:
                print("Enocean: packet type %s not supported (data: %s)"%(packet.type, ''.join(format(x, ' 02x') for x in packet.data)))
    

    def packESP3packet(self, type, data, optData):
        txBuffer = bytearray()
        dataLengthHigh = 0
        dataLengthLow = 0

        dataLengthHigh, dataLengthLow = splitIntIn2Bytes(len(data), 'big')
        
        #SYNC
        txBuffer.append(self.esp3.SYNC_BYTE)
        #header
        txBuffer.append(dataLengthHigh)
        txBuffer.append(dataLengthLow)
        txBuffer.append(len(optData))
        txBuffer.append(type)
        #CRC header
        txBuffer.append(self.esp3.calcCRC8sum(txBuffer[1:]))    #check sum is calculated after sync byte until current buffer content (only header so far)
        #data
        if len(data) > 0:
            txBuffer.extend(data)
        #optional data
        if len(optData) > 0:
            txBuffer.extend(optData)
        #CRC data
        txBuffer.append(self.esp3.calcCRC8sum(txBuffer[1+self.esp3.CRC_HEADER_INDEX:]))    #check sum is calculated after sync byte until current buffer content (only header so far)
        #print(''.join(format(x, ' 02x') for x in txBuffer))
        return(txBuffer)
        
    def pollRxBuffer(self):
        #check buffer
        if self.serIf.inWaiting() > 0:
            # read all characters in buffer
            self.rxBuffer = bytearray(self.serIf.read(self.serIf.inWaiting()))
            print("Enocean RX: buffer: " + ''.join(format(x, ' 02x') for x in self.rxBuffer))
            self.logEnocean += ''.join(format(x, ' 02x') for x in self.rxBuffer) + "\r\n"
       

            #loop through buffer and find all telegrams
            index = 0
            while index < len(self.rxBuffer):       
                #Search for sync byte
                while index < len(self.rxBuffer):
                    if (self.rxBuffer[index] == self.esp3.SYNC_BYTE):
                        startIndex = index
                        #print("Enocean RX: Package found at start index %s"%(startIndex))
                        break;  #telegram found => stop searching for sync byte and process telegram
                    else:
                        index += 1
                        continue
                #Skip telegram processing if not sync byte has been found at all
                if index >= len(self.rxBuffer):
                    break

                #Check CRC of header
                if self.rxBuffer[startIndex + self.esp3.CRC_HEADER_INDEX] != self.esp3.calcCRC8sum(self.rxBuffer[startIndex + self.esp3.SYNC_BYTE_INDEX + 1:startIndex + self.esp3.CRC_HEADER_INDEX]):
                    print('Enocean: Rx: CRC of header is incorrect: %s, %s'%(self.rxBuffer[startIndex + self.esp3.CRC_HEADER_INDEX], self.esp3.calcCRC8sum(self.rxBuffer[startIndex + self.esp3.SYNC_BYTE_INDEX + 1:startIndex + self.esp3.CRC_HEADER_INDEX])))
                    index += 1      #ignore this telegram by shifting to next byte to check for sync byte
                    continue
                
                crcDataIndex = startIndex + self.esp3.CRC_HEADER_INDEX + self.esp3.getDataLength(self.rxBuffer[startIndex:]) + self.esp3.getOptDataLength(self.rxBuffer[startIndex:]) + 1

                #set search index to next telegram
                index = crcDataIndex + 1
                
                #Check CRC of data and add telegram to list for further processing
                try:
                    if self.rxBuffer[crcDataIndex] == self.esp3.calcCRC8sum(self.rxBuffer[startIndex + self.esp3.DATA_START_INDEX:crcDataIndex]):
                        #create a new ESP3 packet and add it to list
                        self.rxESP3packetList.append(ESP3_packet())
                        #fill new object with data extracted from received telegram
                        self.rxESP3packetList[-1].type          = self.esp3.getPacketType(self.rxBuffer[startIndex:])
                        self.rxESP3packetList[-1].dataLength    = self.esp3.getDataLength(self.rxBuffer[startIndex:])
                        self.rxESP3packetList[-1].optDataLength = self.esp3.getOptDataLength(self.rxBuffer[startIndex:])
                        self.rxESP3packetList[-1].data          = self.esp3.extractDataBlock(self.rxBuffer[startIndex:])
                        self.rxESP3packetList[-1].optData       = self.esp3.extractOptDataBlock(self.rxBuffer[startIndex:])
                                
                        #print("Enocean RX: Package added to list: " + ''.join(format(x, ' 02x') for x in self.rxBuffer[startIndex:crcDataIndex]))
                        continue
                    else:
                        print('Enocean Rx: CRC of data is incorrect: %s, %s'%(self.rxBuffer[crcDataIndex], self.esp3.calcCRC8sum(self.rxBuffer[startIndex + self.esp3.DATA_START_INDEX:crcDataIndex])))
                        continue    #skip this telegram. Index is already set to next telegram
                except:
                    print('Enocean Rx: CRC position calculation failed')
                    continue        #skip this telegram. Index is already set to next telegram
    
            #Header and data are valid: further processing of data and optional data
            self.unpackESP3packet()
        else:
            #skip rx processing if rx-buffer is empty
            return

    def sTxStateSend(self):
        #COMMON COMMANDs to TCM310 enocean host module
        if len(self.txCommonComandList) > 0:
            commandCode = self.txCommonComandList.pop(0)
            cmdData = bytearray()
            
            #build data depending on command code
            if (commandCode == self.esp3.CO_RD_IDBASE):
                cmdData.append(commandCode)
            else:
                print("Enocean driver: command code <%s> is not supported"%(commandCode))    
                
            #send command to enocean TCM310 chip
            txBuffer = self.packESP3packet(self.esp3.COMMON_COMMAND, cmdData, bytearray())
            #print("Enocean TX: Common CMD:" + ''.join(format(x, ' 02x') for x in txBuffer))
            self.serIf.write(txBuffer)
            
            return

        #RADIO telegram sending to enocean modules (only once host ID is set)
        if (self.hostID != self.INVALID_HOST_ID):
            for deviceID in self.deviceList:        #check whether packages need to be sent out
                if len(self.deviceList[deviceID].packetTypeRadio.txDataList) > 0:
                    data, optData = self.deviceList[deviceID].packetTypeRadio.txDataList.pop(0)
                    txBuffer = self.packESP3packet(self.esp3.RADIO, data, optData)
                    print("Enocean TX: buffer:" + ''.join(format(x, ' 02x') for x in txBuffer))
                    self.serIf.write(txBuffer)
                    self.activeTxState = "sTxStateWait"
                    
                    self.txWaitTimeStart = time.time()
                    break;

        return
        
    def sTxStateWait(self):
        #wait until trying to send another packet
        if time.time() >= (self.txWaitTimeStart + self.esp3.ESP3_PACKET_TIMEOUT):
            self.activeTxState = "sTxStateSend"
        
        return
    

    def update(self):
        #check receive buffer every update cycle
        self.pollRxBuffer()


        self.txStatemachine[self.activeTxState]()
        if (self.activeTxStateOld != self.activeTxState):
           self.activeTxStateOld = self.activeTxState
           #print("Enocean TX state: " + self.activeTxState)
        