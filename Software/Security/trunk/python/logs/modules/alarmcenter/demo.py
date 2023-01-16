#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/modules/alarmcenter/demo.py

import serial

try: 
    serIf = serial.Serial(
        port='/dev/serial0',
        baudrate=57600,
        parity=serial.PARITY_NONE,
        timeout = 5.0,                 #Python 3: wait in read-Thread
        interCharTimeout = 0.1,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    #from Rasbien Jessie on the interface is open already by calling the constructor. So check first before open it (compatibility with older versions)
    if (serIf.isOpen() == False):
        serIf.open()

    #self.serIf.open()
except Exception as err:
    print("Enocean: error open serial port: {0}".format(err))

#flush current buffer
if serIf.isOpen():
    try:
        serIf.flush()    #PySerial 3.0 flush output buffer, aborting current output 
    except Exception as err:
        print("Enocean:  error communicating...: {0}".format(err))
        serIf.close()
else:
    print("Enocean: cannot open serial port")

print("waiting for RX")
print(serIf.read())
print("Nothing received...")
