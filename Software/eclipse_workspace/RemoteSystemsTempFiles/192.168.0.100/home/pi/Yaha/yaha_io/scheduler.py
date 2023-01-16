#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import enocean.protocol.driver

class yahaEnoceanIOpoint():
    "Representation of a single IO point"    
    def __init__(self):
        self.processTag = None
        self.moduleID = None
        self.hostChannel = None
        self.direction = None
        self.functionType = None
        self.functionVariable = None
        self.functionTypeOptionString = None
        self.processTagOldValue = None
        self.enoceanDevice = None


class yahaEnoceanIOwrapper():
    "Specific IO handler for Enocean IOs"
    def __init__(self, PDI):
        self.MODULE_ID_INDEX = 0
        self.DIRECTION_INDEX = 1
        self.FUNCTION_TYPE_INDEX = 2
        self.FUNCTION_TYPE_OPTIONS_INDEX = 3
        self.FUNCTION_VARIABLE_INDEX = 4

        self.ioTags = dict()
        self.enoceanManager = enocean.protocol.driver.main()        
        self.PDI = PDI
        
        self.idStringElements = list() 
        self.readTags = dict()
        self.writeTags = dict()

        #get all PDI tags of a owner 'enocean' which a channel configured. This is used to teach different actuators with different sender IDs as the often do not allow selective destinationIDs
        self.hostChannels = PDI.getTagHostChannels('enocean')  #"tag" : owner
        try:
            self.enoceanManager.hostID = self.PDI.hostIDsaved   #this host ID is saved in PDI and used just in case read base ID fails
        except Exception, self.e:
            print "IO: hostIDsaved: " + str(self.e)

        #get all PDI tags where enocean is specified as owner => all these tags will be handled by the enocean driver
        self.ioTags = PDI.getTagDeviceIDs('enocean')  #"tag" : ID
        for tag in self.ioTags:
            try:
                #owner ID is formated like: moduleID.direction(in/out).functionType.variable: e.g.: ffdf7880.OUT.F6_02_01.rockerB0
                idStringElements = self.ioTags[tag].split(".")
                #populate read and write list with object which should be handled by the driver
                if idStringElements[self.DIRECTION_INDEX].lower() == "in":
                    self.readTags[tag] = yahaEnoceanIOpoint()
                    self.readTags[tag].processTag = tag
                    self.readTags[tag].moduleID = idStringElements[self.MODULE_ID_INDEX]
                    self.readTags[tag].hostChannel = self.hostChannels[tag]
                    self.readTags[tag].direction = idStringElements[self.DIRECTION_INDEX]
                    self.readTags[tag].functionType = idStringElements[self.FUNCTION_TYPE_INDEX]
                    self.readTags[tag].functionVariable = idStringElements[self.FUNCTION_VARIABLE_INDEX]
                    self.readTags[tag].functionTypeOptionString = idStringElements[self.FUNCTION_TYPE_OPTIONS_INDEX]

                    self.readTags[tag].enoceanDevice = self.enoceanManager.addDevice(self.readTags[tag].moduleID, self.readTags[tag].hostChannel)
                    self.enoceanManager.addDeviceFunctionType(self.readTags[tag].moduleID, self.readTags[tag].functionType)
                else:
                    self.writeTags[tag] = yahaEnoceanIOpoint()
                    self.writeTags[tag].processTag = tag
                    self.writeTags[tag].moduleID = idStringElements[self.MODULE_ID_INDEX]
                    self.writeTags[tag].hostChannel = self.hostChannels[tag]
                    self.writeTags[tag].direction = idStringElements[self.DIRECTION_INDEX]
                    self.writeTags[tag].functionType = idStringElements[self.FUNCTION_TYPE_INDEX]
                    self.writeTags[tag].functionVariable = idStringElements[self.FUNCTION_VARIABLE_INDEX]
                    self.writeTags[tag].functionTypeOptionString = idStringElements[self.FUNCTION_TYPE_OPTIONS_INDEX]
                    
                    self.writeTags[tag].enoceanDevice = self.enoceanManager.addDevice(self.writeTags[tag].moduleID, self.writeTags[tag].hostChannel)
                    self.enoceanManager.addDeviceFunctionType(self.writeTags[tag].moduleID, self.writeTags[tag].functionType)

            except Exception, self.e:
                print "IO: error in PDI owner ID for enocean: " + str(self.e)            

    def readInputs(self):
        self.enoceanManager.update()
        self.PDI.logEnocean = self.enoceanManager.logEnocean

        #go through all tags which should be read from io driver and write current value directly into PDI
        for tag in self.readTags:
            #EXAMPLE: PDI.switch1 = enButton.packetTypeRadio.getTagValue('F6_02_01','rockerB0')
            setattr(self.PDI, self.readTags[tag].processTag, self.readTags[tag].enoceanDevice.packetTypeRadio.getTagValue(self.readTags[tag].functionType, self.readTags[tag].functionVariable))
    
    def writeOutputs(self):
        for tag in self.writeTags:
            #first check whether enocean transmitter is ready
            if (self.writeTags[tag].enoceanDevice.packetTypeRadio.isReady() <> 1):
                break; 
            
            #get current value from PDI
            currentValue = getattr(self.PDI, self.writeTags[tag].processTag)
            #see if it has been changed since last write to enocean module
            if currentValue <> self.writeTags[tag].processTagOldValue:
                self.writeTags[tag].enoceanDevice.packetTypeRadio.setTagValue(self.writeTags[tag].functionType, self.writeTags[tag].functionVariable, self.writeTags[tag].functionTypeOptionString, currentValue)
                self.writeTags[tag].processTagOldValue = currentValue

class main():
    "IO scheduler"
    def __init__(self, PDI):
        self.PDI = PDI
        self.ioDriverList = dict()
         
        #initialize all supported IO drivers:
        self.ioDriverList['enocean'] = yahaEnoceanIOwrapper(self.PDI)
        
      
    def readInputs(self):
        #loop through all registered drivers and activate read function
        for driver in self.ioDriverList:
            self.ioDriverList[driver].readInputs()
  
    
    def writeOutputs(self):
        #loop through all registered drivers and activate write function
        for driver in self.ioDriverList:
            self.ioDriverList[driver].writeOutputs()
  

