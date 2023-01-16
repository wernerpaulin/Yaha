#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import light

class main():
    "Standard device manager"
    def __init__(self, PDI):
        self.PDI = PDI
        
        #IO-Type name space: SD.light.kitchen.ioCtrl.on
        self.SD_INDEX = 0
        self.SD_TYPE_INDEX = 1
        self.SD_UNIQUE_NAME_INDEX = 2
        self.SD_INTERFACE_GROUP_INDEX = 3
        self.SD_INTERFACE_VARIABLE_INDEX = 4
        
        
        #get all PDI tags where a standard device is configured as ioType
        self.standardDeviceTags = self.PDI.getTagStandardDeviceTags()

        #create a list of all standard devices
        self.standardDevices = dict()
        for tag in self.standardDeviceTags:
            self.idStringElements = self.standardDeviceTags[tag].split('.')
            
            #create instance of standard device according to its type (light, shutter,...)
            if (self.idStringElements[self.SD_TYPE_INDEX] == 'light'):
                #create instance for a certain device name only once
                if self.idStringElements[self.SD_UNIQUE_NAME_INDEX] not in self.standardDevices:
                    self.standardDevices[self.idStringElements[self.SD_UNIQUE_NAME_INDEX]] = light.Manager(self.PDI)
                
                self.standardDevices[self.idStringElements[self.SD_UNIQUE_NAME_INDEX]].setInterfaceToPDI(self.idStringElements[self.SD_INTERFACE_GROUP_INDEX], self.idStringElements[self.SD_INTERFACE_VARIABLE_INDEX], tag)

    #update all standard devices
    def update(self):
        for device in self.standardDevices:
            self.standardDevices[device].update()