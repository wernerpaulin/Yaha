#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import serial

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



try: 
    serIf.open()
except Exception, e:
    print "Error open serial port: " + str(e)
    exit()

if serIf.isOpen():
    try:
        serIf.flushInput() #flush input buffer, discarding all its contents
        serIf.flushOutput()#flush output buffer, aborting current output 
    
        while True:
            while serIf.inWaiting() > 0:
                response = serIf.read(serIf.inWaiting()).encode('hex')
                print("read data: " + response)
          
    
    

    except Exception, e1:
        print "error communicating...: " + str(e1)
        serIf.close()

else:
    print "Cannot open serial port"

