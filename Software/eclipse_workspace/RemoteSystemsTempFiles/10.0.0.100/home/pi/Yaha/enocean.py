#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/enocean.py
#python /home/pi/Yaha/yaha_main.py

from struct import *
from py_utilities import *
import serial
import time

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
    
class EnoceanDevice():
    "Enocean - each physical device is represented by this class"
    def __init__(self):
        self.packetTypeRadio = PacketTypeRadio()
        self.packetTypeRadio.hostID = None


class manager():
    "Enocean - manages serial communication and forwards frames for further processing to corresponding device"
    def __init__(self):
        self.esp3 = ESP3()
        self.deviceList = dict()                #this list contains all known devices referenced by their sender ID
        self.unknownDeviceList = dict()         #this list contains all devices from which telegrams have been received but not actions are implemented
        self.logEnocean = ""
        self.rxESP3packetList = list()
        self.rxBuffer = bytearray()

        self.txStatemachine = {
                             "sTxStateSend": self.sTxStateSend,
                             "sTxStateWait": self.sTxStateWait
                            }
        self.activeTxState = "sTxStateSend"
        self.activeTxStateOld = ""
        self.txWaitTimeStart = 0


        #set enocean sender ID to first 4 digits of mac address 
        self.hostID = getHwAddr('eth0')
        self.hostID = self.hostID.split(":")
        self.hostID = self.hostID[0:4]
        self.hostID = ''.join(self.hostID)  #join byte list to a string

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



    def addDevice(self, deviceID='ffffffff', funcTypeRPS=None, funcType1BS=None, funcType4BS=None, funcTypeVLD=None):
        #create device
        deviceID = deviceID.lower()                 #ID is always considered lower case
        self.deviceList[deviceID] = EnoceanDevice()
        self.deviceList[deviceID].packetTypeRadio.hostID = self.hostID  #ID of this Enocean host
        self.deviceList[deviceID].packetTypeRadio.ownID = deviceID
        
        #set specific profile which is supported by this device depending on the radio variant (RORG)
        if funcTypeRPS <> None:
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_RPS)[2:], funcTypeRPS)
        
        if funcType1BS <> None:
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_1BS)[2:], funcType1BS)

        if funcType4BS <> None:
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_4BS)[2:], funcType4BS)

        if funcTypeVLD <> None:
            self.deviceList[deviceID].packetTypeRadio.setSupportedProfile(hex(self.deviceList[deviceID].packetTypeRadio.RORG_VLD)[2:], funcTypeVLD)

        return(self.deviceList[deviceID])

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
                if packet.data[0] == self.esp3.RET_OK:
                    pass    #do nothing with this return code as ESP3 does not tell from which sender it came 
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
        #check whether packages need to be sent out
        for deviceID in self.deviceList:
            if len(self.deviceList[deviceID].packetTypeRadio.txDataList) > 0:
                data, optData = self.deviceList[deviceID].packetTypeRadio.txDataList.pop(0)
                txBuffer = self.packESP3packet(self.esp3.RADIO, data, optData)
                print("Enocean TX: buffer:" + ''.join(format(x, ' 02x') for x in txBuffer))
                self.serIf.write(txBuffer)
                self.activeTxState = "sTxStateWait"
                #print("Enocean TX: Device <%s>: data:%s"%(deviceID, ''.join(format(x, ' 02x') for x in data)))
                
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
           print("Enocean TX state: " + self.activeTxState)
        
        



# Module testing
if __name__ == "__main__":
    print("!!! Test mode active !!!")
    enoceanMan = manager()
    mydevice = enoceanMan.addDevice('0029af6c', funcTypeRPS = 'F6_02_01', funcType1BS = None, funcType4BS = 'None', funcTypeVLD = None)

    enoceanMan.update()
    
    if len(enoceanMan.unknownDeviceList) > 0:
        print(enoceanMan.unknownDeviceList)

    #mydevice.packetTypeRadio.setTagValue('F6_02_01','switch',True)
    print("mydevice.rockerB0 = " + str(mydevice.packetTypeRadio.getTagValue('F6_02_01','rockerB0')))
    print("mydevice.rockerB1 = " + str(mydevice.packetTypeRadio.getTagValue('F6_02_01','rockerB1')))
    
    
    
     