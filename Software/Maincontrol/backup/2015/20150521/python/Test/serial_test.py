#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import serial
import datetime, threading, time
import socket               # Import socket module
import json


# configure the serial connections (the parameters differs on the device you are connecting to)
serIf = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=57600,
    parity=serial.PARITY_NONE,
    timeout = 0.1,
    interCharTimeout = 0.1,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)



IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
 
RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
RXsocket.bind((IP_ADR, PORT_Client_to_Server))

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def Logger():
    global response

    while True:    
        data, addr = RXsocket.recvfrom(1024) # buffer size is 1024 bytes
        rxData = json.loads(data)
        
        #TXsocket.sendto(response, (IP_ADR, PORT_Server_to_Client))
    
    
    
def EnOceanDriver():    
    global response
    
    while True:
        while serIf.inWaiting() > 0:
            response = serIf.read(serIf.inWaiting()).encode('hex')
            print("read data: " + response)
            TXsocket.sendto(response, (IP_ADR, PORT_Server_to_Client))
          



try: 
    serIf.open()
except Exception, e:
    print "Error open serial port: " + str(e)
    exit()

if serIf.isOpen():
    try:
        serIf.flushInput() #flush input buffer, discarding all its contents
        serIf.flushOutput()#flush output buffer, aborting current output 

        enoceanThread = threading.Thread(target=EnOceanDriver)
        enoceanThread.start()

        loggingThread = threading.Thread(target=Logger)
        loggingThread.start()
    
    except Exception, e1:
        print "error communicating...: " + str(e1)
        serIf.close()

else:
    print "Cannot open serial port"
    
    
    

