#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

class Manager():
    class user():
        "User input interface"
        def __init__(self):
            self.on = None
            self.off = None
            self.learning = None

    class ioCtrl():
        "Interface to be connected to the IO driver to control the switch"
        def __init__(self):
            self.offOn = None
            self.learning = None
        
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

    #assign string names of PDI variables to user, ioCtrl and status
    def setInterfaceToPDI(self, ifGroup, ifVar, pdiProcessTag): #e.g.: 'user','on','light1on'
        try:
            ifGroupObj = getattr(self, ifGroup) #get access to user object in this class
            setattr(ifGroupObj, ifVar, pdiProcessTag)   #set attribute of object: user.on = 'light1on'
        except:
            return

    def update(self):
        #Scan user inputs and set io control variables in PDI (io-driver listens to this variables due to ownerID
        #no every channel might be configured - ignore not connected channels
        try:
            if getattr(self.pdi, self.user.on) == 1:
                setattr(self.pdi, self.user.on, 0)
                setattr(self.pdi, self.ioCtrl.offOn, 1)
        except:
            return
        
        try:
            if getattr(self.pdi, self.user.off) == 1:
                setattr(self.pdi, self.user.off, 0)
                setattr(self.pdi, self.ioCtrl.offOn, 0)
        except:
            return

        #Scan user inputs and set io control variables in PDI (io-driver listens to this variables due to ownerID
        try:
            if getattr(self.pdi, self.user.learning) == 1:
                setattr(self.pdi, self.user.learning, 0)
                setattr(self.pdi, self.ioCtrl.learning, 1)
            else:
                setattr(self.pdi, self.user.learning, 0)
                setattr(self.pdi, self.ioCtrl.learning, 0)
        except:
            return
            