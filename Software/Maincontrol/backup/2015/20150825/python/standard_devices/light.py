#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import time

class Manager():
    BUTTON_PRESS_DURATION = 0.0 #seconds
    ALIVE_CHECK_INTERVAL = 1.0
    
    class user():
        "User input interface"
        def __init__(self):
            self.on = None
            self.off = None
            self.inching = None

    class ioCtrl():
        "Interface to be connected to the IO driver to control the switch"
        def __init__(self):
            self.on = None
            self.off = None
        
    class status():
        "Current status data of light"
        def __init__(self):
            self.energy = None
            self.onTime = None
            self.switchedOn = None
            self.dimmValue = None
            self.errorLamp = None
            self.errorInternal = None
            self.errorExternal = None
    
    #all values given by name in order to use get and set functions to write into PDI
    def __init__(self, PDI):
        self.pdi = PDI
        self.user = Manager.user()
        self.ioCtrl = Manager.ioCtrl()
        self.status = Manager.status()

        self.updateStatemachine = {
                                   "sUpdateStateIdle": self.sUpdateStateIdle,
                                   "sUpdateStateRelease": self.sUpdateStateRelease
                                   }
        self.activeUpdateState = "sUpdateStateIdle"
        self.pressStartTime = 0


    #assign string names of PDI variables to user, ioCtrl and status
    def setInterfaceToPDI(self, ifGroup, ifVar, pdiProcessTag): #e.g.: 'user','on','light1on'
        ifGroupObj = getattr(self, ifGroup) #get access to user object in this class
        setattr(ifGroupObj, ifVar, pdiProcessTag)   #set attribute of object: user.on = 'light1on'


    def sUpdateStateIdle(self):
        #Scan user inputs and set io control variables in PDI (io-driver listens to this variables due to ownerID
        if getattr(self.pdi, self.user.on) == 1:
            setattr(self.pdi, self.user.on, 0)
            setattr(self.pdi, self.ioCtrl.on, 1)
        
        if getattr(self.pdi, self.user.off) == 1:
            setattr(self.pdi, self.user.off, 0)
            setattr(self.pdi, self.ioCtrl.off, 1)

        self.pressStartTime = time.time()
        self.activeUpdateState = "sUpdateStateRelease"

    def sUpdateStateRelease(self):
        #wait until time has elapsed
        if (time.time() < self.pressStartTime + self.BUTTON_PRESS_DURATION):
            return
        
        #reset outputs
        if getattr(self.pdi, self.ioCtrl.on) == 1:
            setattr(self.pdi, self.ioCtrl.on, 0)
        
        if getattr(self.pdi, self.ioCtrl.off) == 1:
            setattr(self.pdi, self.ioCtrl.off, 0)
        
        #wait for next user interation
        self.activeUpdateState = "sUpdateStateIdle"

    def update(self):
       try:
           self.updateStatemachine[self.activeUpdateState]()
       except Exception, self.e:
           print "StandardDevice: " + str(self.e)            
