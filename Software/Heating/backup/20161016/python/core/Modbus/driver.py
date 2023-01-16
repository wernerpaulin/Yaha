#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py
#python3 /home/pi/Yaha/core/Modbus/driver.py

"http://pymodbus.readthedocs.io/en/latest/examples/synchronous-client.html"
import threading
import logging
import time


from pymodbus3.client.sync import ModbusTcpClient as ModbusClient

MODBUS_TIMEOUT = 0.5
MODBUS_PORT_NR = 502
ANALOG_IN = "ai"
DIGITAL_IN = "di"
DIGITAL_OUT = "do"

class main():
    "Specific IO handler for Modbus IOs"
    def __init__(self, PDI):
        self.CLIENT_IP_INDEX = 0
        self.IO_TYPE_INDEX = 1
        self.ADDRESS_INDEX = 2
        self.MAX_RESISTANCE_INDEX = 3
        self.MAX_VALUE_INDEX = 4
        
        self.PDI = PDI
        
        self.ioTags = dict()
        self.idStringElements = list() 
        self.readTags = dict()
        self.writeTags = dict()   
        
        self.clientList = dict()    #"IP-Adr" : class 

        #get all PDI tags where MODBUS is specified as owner => all these tags will be handled by the MODBUS driver
        self.ioTags = PDI.getTagDeviceIDs('MODBUS')  #"tag" : ID
        for tag in self.ioTags:
            try:
                #device IDs are formated like: CLIENT-IP:C0:A8:00:5C.AI.0x0000.rmax:2250.vmax:45000
                self.idStringElements = self.ioTags[tag].split(".")
                
                #convert client IP address from hex to decimal string
                clientIPhex = self.idStringElements[self.CLIENT_IP_INDEX].lower()
                clientIPint = "{0}.{1}.{2}.{3}".format( int(clientIPhex[10:12],16), 
                                                        int(clientIPhex[13:15],16), 
                                                        int(clientIPhex[16:18],16), 
                                                        int(clientIPhex[19:21],16) )
                #create an client infrastructure for this ip address if it does not yet exists
                if (clientIPint not in self.clientList):
                    self.clientList[clientIPint] = modbusClient(clientIPint, MODBUS_PORT_NR, self.PDI)

                #get IO type to which this tag belongs to: ANALOG_IN, DIGITAL_IN, DIGITAL_OUT
                tagIoType = self.idStringElements[self.IO_TYPE_INDEX].lower()
                #create ioType infrastructure if it does not yet exists
                if (tagIoType not in self.clientList[clientIPint].ioTypes):
                    self.clientList[clientIPint].ioTypes[tagIoType] = ioType()
                    self.clientList[clientIPint].ioTypes[tagIoType].minAdr = 0xFFFF     #drag indicator initialization
                    self.clientList[clientIPint].ioTypes[tagIoType].maxAdr = 0x0000     #drag indicator initialization
                
                #generate address range (min/max) for selected and optimized Modbus telegrams 
                tagAddress = int(self.idStringElements[self.ADDRESS_INDEX], 16) #convert hex string to number
                
                if (tagAddress < self.clientList[clientIPint].ioTypes[tagIoType].minAdr):
                    self.clientList[clientIPint].ioTypes[tagIoType].minAdr = tagAddress     #smallest address used of all modbus tags of the current IO-type

                if (tagAddress > self.clientList[clientIPint].ioTypes[tagIoType].maxAdr):
                    self.clientList[clientIPint].ioTypes[tagIoType].maxAdr = tagAddress     #biggest address used of all modbus tags of the current IO-type

                #create tag specific infrastructure for IO point
                self.clientList[clientIPint].ioTypes[tagIoType].ioList[tag] = ioPoint()
                self.clientList[clientIPint].ioTypes[tagIoType].ioList[tag].address = tagAddress
                self.clientList[clientIPint].ioTypes[tagIoType].ioList[tag].processTag = tag

                #optional: scaling values for resistor measurement (temperature module)
                try:
                    self.clientList[clientIPint].ioTypes[tagIoType].ioList[tag].resistorMax = int(self.idStringElements[self.MAX_RESISTANCE_INDEX].split(":")[1])
                    self.clientList[clientIPint].ioTypes[tagIoType].ioList[tag].valueMax = int(self.idStringElements[self.MAX_VALUE_INDEX].split(":")[1])
                except:
                    self.clientList[clientIPint].ioTypes[tagIoType].ioList[tag].resistorMax = None
                    self.clientList[clientIPint].ioTypes[tagIoType].ioList[tag].valueMax = None

            except Exception as e:
                print("IO: error in PDI owner ID for MODBUS: {0}".format(e))            



        #start driver only if PDI tags are configured for ABE
        if (len(self.ioTags) > 0):
            self.start()

    def start(self):
        for clients in self.clientList:
            self.clientList[clients].connect()
    
    def readInputs(self):
        #go through all tags which should be read from io driver and write current value directly into PDI
        for clients in self.clientList:
            self.clientList[clients].readInputs()


    def writeOutputs(self):
        #go through all write tags and see if it has been changed since last write
        for clients in self.clientList:
            self.clientList[clients].writeOutputs()


        
class modbusClient():
    #init
    def __init__(self,ipAdr, portNr, PDI):
        #debugging logging
        #logging.basicConfig()
        #self.mbLog = logging.getLogger()
        #self.mbLog.setLevel(logging.DEBUG)
        
        self.modbusIPadr = ipAdr
        self.modbusPortNr = portNr
        self.PDI = PDI
        self.mbClientHandler = None     
        
        self.modbusThreadID = 0
        self.modbusStartTime = 0
            
        self.ioTypes = dict()

    
    def connect(self):
        #try to close any open connection
        try:
            self.mbClientHandler.close()
        except:
            pass
        
        #Connect to Modbus client
        self.mbClientHandler = ModbusClient(self.modbusIPadr, port=self.modbusPortNr)
        self.mbClientHandler.connect()

        #reset expired watchdog        
        try:
            wr = self.mbClientHandler.write_register(0x1044, 0xC1)
            if (wr.function_code >= 0x80):
                print("Modbus (IP: {0}): reset watchdog failed: {1}".format(self.modbusIPadr, wr))
        except Exception as e:
            #print("Modbus (IP: {0}): write_register() failed {1}".format(self.modbusIPadr, e))
            self.mbClientHandler.close()
            #reconnect will happen with next write operation
                
        
    def readInputs(self):
        try:
            #check if communication has been finished while main cycle has sleeping
            if (self.modbusThreadID.isAlive() == False):
                #print("Modbus communication time: {0}".format(time.time() - self.modbusStartTime))

                #copy latest received (triggered during write cycle) values to PDI
                if (DIGITAL_IN in self.ioTypes):
                    for tag in self.ioTypes[DIGITAL_IN].ioList:
                        #during establishing the Modbus connection it can be that the pymodbus3 library returns NoneType which is not allowed to be copied on PDI variables
                        if (self.ioTypes[DIGITAL_IN].ioList[tag].currentIOvalue is not None):
                            setattr(self.PDI, self.ioTypes[DIGITAL_IN].ioList[tag].processTag, self.ioTypes[DIGITAL_IN].ioList[tag].currentIOvalue)

                if (ANALOG_IN in self.ioTypes):
                    for tag in self.ioTypes[ANALOG_IN].ioList:
                        #during establishing the Modbus connection it can be that the pymodbus3 library returns NoneType which is not allowed to be copied on PDI variables
                        if (self.ioTypes[ANALOG_IN].ioList[tag].currentIOvalue is not None):
                            setattr(self.PDI, self.ioTypes[ANALOG_IN].ioList[tag].processTag, self.ioTypes[ANALOG_IN].ioList[tag].currentIOvalue)
            
            elif ( (time.time() - self.modbusStartTime) >= MODBUS_TIMEOUT ):
                print("Modbus (IP: {0}): timeout".format(self.modbusIPadr))
                try:
                    #close and reopen again
                    self.mbClientHandler.close()
                    self.connect()
                except:
                    pass
            else:
                print("Modbus (IP: {0}): not finished in one cycle. Elapsed time: {1}".format(self.modbusIPadr, (time.time() - self.modbusStartTime)))
        except:
            #thread has not been started (could happen after boot up when write happens after the first cycle)
            pass
    
     
    def writeOutputs(self):
        #copy tags to write from PDI into local IO image - currently only Digital-Out is supported
        if (DIGITAL_OUT in self.ioTypes):
            for tag in self.ioTypes[DIGITAL_OUT].ioList:
                self.ioTypes[DIGITAL_OUT].ioList[tag].currentIOvalue = getattr(self.PDI, self.ioTypes[DIGITAL_OUT].ioList[tag].processTag)
                if (self.ioTypes[DIGITAL_OUT].ioList[tag].currentIOvalue == 0):
                    self.ioTypes[DIGITAL_OUT].ioList[tag].currentIOvalue = False
                else:
                    self.ioTypes[DIGITAL_OUT].ioList[tag].currentIOvalue = True
                

        #before starting another communication thread, check whether the old one has been terminated (= thread function finished)
        try:
            if (self.modbusThreadID.isAlive() == True):
                return
        except:
            #thread handle invalid = thread not yet started => also ok. Continue with starting a new thread
            pass
        
        #entire Modbus read/write communication happens here: write is called at the end of the cycle time which gives enough time for communication until the new cycle starts (read data are then already available)
        try:
            #start synchronous modbus read/write as thread to not block cyclic system
            self.modbusThreadID = threading.Thread(target=self.modbusHandlerThread)
            self.modbusStartTime = time.time()
            self.modbusThreadID.start()
            return
        
        except Exception as e:
            print("Modbus (IP: {0}): starting Modbus thread failed: {1}".format(self.modbusIPadr, e))
            return  

    def modbusHandlerThread(self):
        #write digital outputs if such tags exists
        if (DIGITAL_OUT in self.ioTypes):
            #create array of bits which will hold all values which need to be written to the Modbus client
            nbIOchannels = self.ioTypes[DIGITAL_OUT].maxAdr - self.ioTypes[DIGITAL_OUT].minAdr + 1
            digitalOutArray = [False for x in range(nbIOchannels)]

            #fill bit array with values: array index represents address of io point starting at minium address 
            for tag in self.ioTypes[DIGITAL_OUT].ioList:
                try:
                    #determine position within bit array depending on the modbus address with minAdr as offset and write currentIOvalue into array
                    arrayIndex = self.ioTypes[DIGITAL_OUT].ioList[tag].address - self.ioTypes[DIGITAL_OUT].minAdr
                    digitalOutArray[arrayIndex] = self.ioTypes[DIGITAL_OUT].ioList[tag].currentIOvalue
                except Exception as e:
                    print("Modbus (IP: {0}): write digital out address error: {1}: {2}".format(self.modbusIPadr, e, arrayIndex))
            
            #write all digital outputs on Modbus                    
            try:
                wr = self.mbClientHandler.write_coils(self.ioTypes[DIGITAL_OUT].minAdr, digitalOutArray)
                if (wr.function_code >= 0x80):
                    print("Modbus (IP: {0}): write digital out communication error: {1}".format(self.modbusIPadr, wr))
            except Exception as e:
                #print("Modbus (IP: {0}): write_coils() failed {1}".format(self.modbusIPadr, e))
                #close and reopen again
                self.mbClientHandler.close()
                self.connect()
                return
                
                
        #read digital inputs if such tags exists
        if (DIGITAL_IN in self.ioTypes):
            nbIOchannels = self.ioTypes[DIGITAL_IN].maxAdr - self.ioTypes[DIGITAL_IN].minAdr + 1
            try:
                rr = self.mbClientHandler.read_discrete_inputs(self.ioTypes[DIGITAL_IN].minAdr, count=nbIOchannels)
                
                if (rr.function_code >= 0x80):
                    print("Modbus (IP: {0}): read digital in communication error: {1}".format(self.modbusIPadr, rr))
                else:
                    #successful read of digital in channels
                    for tag in self.ioTypes[DIGITAL_IN].ioList:
                        try:                
                            #determine position within bit array depending on the modbus address with minAdr as offset and read bit value and copy it into currentIOvalue
                            arrayIndex = self.ioTypes[DIGITAL_IN].ioList[tag].address - self.ioTypes[DIGITAL_IN].minAdr
                            self.ioTypes[DIGITAL_IN].ioList[tag].currentIOvalue = rr.bits[arrayIndex]
                        except Exception as e:
                            print("Modbus (IP: {0}): read digital in address error: {1}: {2}".format(self.modbusIPadr, e, arrayIndex))
            except Exception as e:
                #print("Modbus (IP: {0}): read_discrete_inputs() failed {1}".format(self.modbusIPadr, e))
                #close and reopen again
                self.mbClientHandler.close()
                self.connect()
                return
                            

        #read analog inputs if such tags exists
        if (ANALOG_IN in self.ioTypes):
            nbIOchannels = self.ioTypes[ANALOG_IN].maxAdr - self.ioTypes[ANALOG_IN].minAdr + 1

            try:
                rr = self.mbClientHandler.read_input_registers(self.ioTypes[ANALOG_IN].minAdr, count=nbIOchannels)
                
                if (rr.function_code >= 0x80):
                    print("Modbus (IP: {0}): read analog in communication error: {1}".format(self.modbusIPadr, rr))
                else:
                    #successful read of analog in channels
                    for tag in self.ioTypes[ANALOG_IN].ioList:
                        try:                
                            #determine position within bit array depending on the modbus address with minAdr as offset and read bit value and copy it into currentIOvalue
                            arrayIndex = self.ioTypes[ANALOG_IN].ioList[tag].address - self.ioTypes[ANALOG_IN].minAdr
                            #print(rr.registers[arrayIndex])
                            #try to scale received value
                            try:
                                tempIOvalue = rr.registers[arrayIndex]  #this value is not yet scales
                                self.ioTypes[ANALOG_IN].ioList[tag].currentIOvalue = self.ioTypes[ANALOG_IN].ioList[tag].resistorMax / self.ioTypes[ANALOG_IN].ioList[tag].valueMax * tempIOvalue
                                
                            except:
                                self.ioTypes[ANALOG_IN].ioList[tag].currentIOvalue = rr.registers[arrayIndex]   #no scaling information available us direct value from received register
                        except Exception as e:
                            print("Modbus (IP: {0}): read analog in address error: {1}: {2}".format(self.modbusIPadr, e, arrayIndex))
            except Exception as e:
                #print("Modbus (IP: {0}): read_input_registers() failed {1}".format(self.modbusIPadr, e))
                #close and reopen again
                self.mbClientHandler.close()
                self.connect()
                return


class ioType():
    def __init__(self):
        self.ioList = dict()
        self.minAdr = 0x0000
        self.maxAdr = 0x0000

class ioPoint():
    "CLIENT-IP:C0:A8:00:5C.AI.0x0000.rmax:2250.vmax:45000"    
    def __init__(self):
        self.address = None
        self.resistorMax = None
        self.valueMax = None
        self.processTag = None
        self.currentIOvalue = None         #last IO value read form the bus
        

