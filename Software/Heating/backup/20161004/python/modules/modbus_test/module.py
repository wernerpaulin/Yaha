#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py

"http://pymodbus.readthedocs.io/en/latest/examples/synchronous-client.html"
import threading
import logging
import time

from core.modules.pymodbus3.client.sync import ModbusUdpClient as ModbusClient

MODBUS_TIMEOUT = 1.0


def init(PDI):
    global ModbusClientID
    ModbusClientID = modbusManager('192.168.0.92', 502)
    


def update(PDI):
    global ModbusClientID
    
    #cyclic execution of Modbus
    ModbusClientID.update()
    
    
class modbusManager():
    #init
    def __init__(self,ipAdr, portNr):
        self.modbusIPadr = ipAdr
        self.modbusPortNr = portNr

        #debugging logging
        logging.basicConfig()
        self.mbLog = logging.getLogger()
        self.mbLog.setLevel(logging.DEBUG)

        #Connect to Modbus client
        self.client = ModbusClient(ipAdr, port=portNr)
        self.client.connect()
        
        self.modbusThreadID = 0

        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sMB_READ_WRITE_DATA": self.sMB_READ_WRITE_DATA, 
                             "sMB_READ_WRITE_DATA_WAIT": self.sMB_READ_WRITE_DATA_WAIT 
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""
        self.modbusStartTime = 0
    
    def update(self):
        #execute state machine
        self.statemachine[self.activeState]()
        #logging of state
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           #print("Modbus (IP: {0}): state: {1}".format(self.modbusIPadr, self.activeState))


    def modbusHandlerThread(self):
        """
        rr = self.client.read_coils(1, 1, unit=0x02)
        rq = self.client.write_coil(1, True)
        rr = self.client.read_coils(1,1)
        assert(rq.function_code < 0x80)     # test that we are not an error
        assert(rr.bits[0] == True)          # test the expected value
        
        rq = self.client.write_coils(1, [True]*8)
        rr = self.client.read_coils(1,8)
        assert(rq.function_code < 0x80)     # test that we are not an error
        assert(rr.bits == [True]*8)         # test the expected value
        
        rq = self.client.write_coils(1, [False]*8)
        rr = self.client.read_discrete_inputs(1,8)
        assert(rq.function_code < 0x80)     # test that we are not an error
        assert(rr.bits == [False]*8)         # test the expected value    
        """
        
        self.client.close()

    def sIDLE(self):
        self.activeState = "sMB_READ_WRITE_DATA"

    def sMB_READ_WRITE_DATA(self):
        try:
            #start synchronous modbus read/write as thread to not block cyclic system
            self.modbusThreadID = threading.Thread(target=self.modbusHandlerThread)
            self.modbusThreadID.start()
            self.modbusStartTime = time.time()
            self.activeState = "sMB_READ_WRITE_DATA_WAIT"
            return
        
        except Exception as e:
            print("Modbus (IP: {0}): start failed: {1}".format(self.modbusIPadr, e))
            self.activeState = "sIDLE"
            return       

    def sMB_READ_WRITE_DATA_WAIT(self):
        if (self.modbusThreadID.isAlive() == False):
            #print("Modbus (IP: {0}): thread finished successfully".format(self.modbusIPadr))
            self.activeState = "sIDLE"
        
        elif ( (time.time() - self.modbusStartTime) >= MODBUS_TIMEOUT ):
            print("Modbus (IP: {0}): timeout".format(self.modbusIPadr))
            try:
                self.client.close()
            except:
                pass
            self.activeState = "sIDLE"        
        
        