#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import serial

class Driver:
    'Yaha EnOcean driver: communicates with Enocean devices'

    def __init__(self):
        self.logEnocean = ""
        
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


    def update(self):
        while self.serIf.inWaiting() > 0:
            self.response = self.serIf.read(self.serIf.inWaiting()).encode('hex')
            print("read data: " + self.response)
            self.logEnocean = self.logEnocean + self.response + "\r\n"