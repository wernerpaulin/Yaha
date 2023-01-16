#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import os
import sys
import datetime, time

class Manager:
    'Yaha date and time manager: sets date and time'
    '''
    Setting the date with a CGI call in a python script called by the webserver is not possible due to user access rights (also subprocess is not working)
    '''
    def __init__(self):
        pass
    
    def setDateTimeHandler(self, cmdSetDateTime, setDateString, setTimeString):
        if (cmdSetDateTime == 1):
            cmdSetDateTime = 0

            try:
                #os.system('sudo date -s "2015-11-12 15:35:00"')
                os.system('sudo date -s "' + setDateString + ' ' + setTimeString + ':00"')     #call system shell function: sudo date -s "2004-02-29 16:21:42"
            except:
                print("setting date and time failed")
                
        return cmdSetDateTime 
    
    
    
    def getDate(self):
        return int(float(datetime.datetime.now().strftime("%Y"))), int(float(datetime.datetime.now().strftime("%m"))), int(float(datetime.datetime.now().strftime("%d")))

    def getTime(self):
        return int(float(datetime.datetime.now().strftime("%H"))), int(float(datetime.datetime.now().strftime("%M"))), int(float(datetime.datetime.now().strftime("%S")))
