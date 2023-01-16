#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py
#python /home/pi/Yaha/core/pdi/yaha_pdi.py

import xml.etree.ElementTree as xmlParser
import os


VALUE_TYPE_REAL = "REAL"
VALUE_TYPE_TEXT = "TEXT"
REMANENT_TRUE = "true"
PROCESS_DATA_CFG_ELEMENT_NAME = "./process_data"
PROCESS_TAG_ELEMENT_NAME = "processTag"
ERROR_RESPONSE_TAG_UNKNOWN = "$unkown$"

class ProcessDataImage:
    'Yaha Process Data Image: simplifies handing central process data by using class attributes instead of dictionary strings'

    #creates the database holding the process data image
    def __init__(self, remDataFile): 
        self.__internalPDI = dict()
        self.__internalRemDataFile = remDataFile

    #add items to PDI and initializes them
    def addItemsFromFile(self, pdiDefinitionFile):
        cntItem = 0 #counter used to identify configured item in file in case the process tag name is wrong

        #access xml file
        try:
            pdiTree = xmlParser.parse(pdiDefinitionFile)
            pdiRoot = pdiTree.getroot()
        except:
            self.__internalPDI.clear()
            return

        #read xml configuration of each process tag and build up data structure        
        for processDataCfg in pdiRoot.findall(PROCESS_DATA_CFG_ELEMENT_NAME):
            cntItem += 1    
            #create internal data structure
            try:
                #add process data item to process data image configuration
                processTagName = processDataCfg.find(PROCESS_TAG_ELEMENT_NAME).text
                self.__internalPDI[processTagName] = ProcessDataItem()       #"switch1 : reference to object of class ProcessDataItem"
                
                #add process data item to process data image (live values)
                setattr(self, processTagName, None)       #correct value will be applied with first read action
            except:
                print("Yaha_pdi: name of process tag not found {0}".format(cntItem))

            #read process data configuration
            try:
                #go through entire process tag configuration and apply it generically to internal configuration
                for processTagCfgItem in processDataCfg:
                    #print(processTagCfgItem.tag)
                    #1. check whether element name in cfg file exists in ProcessDataItem (don't create new properties of class just because there is a spelling mistake in configuration file
                    if (getattr(self.__internalPDI[processTagName], processTagCfgItem.tag, None) != None):
                        #2.apply value from configuration file
                        setattr(self.__internalPDI[processTagName], processTagCfgItem.tag, processTagCfgItem.text)
            except:
                print("Yaha_pdi: process tag <{0}> configuration item {1} unknown".format(processTagName, processTagCfg.tag))

        
        #check if a remanent configuration exists for this process tag and overwrite init value of this variable is (still) configured as remanent
        try:
            remXmlTree = xmlParser.parse(self.__internalRemDataFile)
            remXmlRoot = remXmlTree.getroot()
            #loop over all rem data found in rem file        
            for processTagCfg in remXmlRoot:
                processTagName = processTagCfg.tag
                #check whether element stored in file still exists in current process data image
                if processTagName in self.__internalPDI:
                    if (self.__internalPDI[processTagName].valueType == VALUE_TYPE_REAL):
                        self.__internalPDI[processTagName].valueREAL = float(processTagCfg.text)
                    elif (self.__internalPDI[processTagName].valueType == VALUE_TYPE_TEXT):
                        self.__internalPDI[processTagName].valueTEXT = processTagCfg.text
                    else:
                        print("Yaha_pdi init: process tag <{0}> value type {1} not supported".format(self.__internalPDI[processTagName].processTag, self.__internalPDI[processTagName].valueType))
        except Exception, e:
            print("Error loading remanent data xml file: {0}".format(e))
            #restore empty file to ensure successful boot of system
            self.restoreRemanentDataXmlFile()
            return    
            
            
        #copy init values from configuration to live values
        self.read()

    
    #reads current values from the database and updates the PDI class object
    def read(self, tagsToReadList = None):
        #if no specific tags to read are given, read all tags from internal memory which are known
        if (tagsToReadList == None):
            tagsToReadList = dict()
            for processTagName in self.__internalPDI:
                tagsToReadList[self.__internalPDI[processTagName].processTag] = None
                    
            
        #copy values from configuration to live value
        for processTagName in tagsToReadList:
            try:    #watch out for wrongly given tags
                if (self.__internalPDI[processTagName].valueType == VALUE_TYPE_REAL):
                    #copy generically value from internal memory to live value
                    setattr(self, self.__internalPDI[processTagName].processTag, float(self.__internalPDI[processTagName].valueREAL))  #PDI.switch = 0
                    #publish value from internal memory through given tag list
                    tagsToReadList[processTagName] = float(self.__internalPDI[processTagName].valueREAL)
                
                elif (self.__internalPDI[processTagName].valueType == VALUE_TYPE_TEXT):
                    #copy generically value from internal memory to live value
                    setattr(self, self.__internalPDI[processTagName].processTag, self.__internalPDI[processTagName].valueTEXT)
                    #publish value from internal memory through given tag list
                    tagsToReadList[processTagName] = self.__internalPDI[processTagName].valueTEXT
                
                else:
                    print("Yaha_pdi read: process tag <{0}> value type {1} not supported".format(self.__internalPDI[processTagName].processTag, self.__internalPDI[processTagName].valueType))

            except Exception, self.e:
                tagsToReadList[processTagName] = ERROR_RESPONSE_TAG_UNKNOWN
                print("Yaha_pdi read: process tag <{0}> error: {1}".format(processTagName, self.e))
                

        return tagsToReadList   #give back list with read values

    #writes values from the class object to the database
    def write(self, tagsToWriteList = None):
        #if no specific tags to write is given, write all tags from internal memory which are known
        if (tagsToWriteList == None):
            tagsToWriteList = dict()
            for processTagName in self.__internalPDI:
                tagsToWriteList[self.__internalPDI[processTagName].processTag] = None       #live value will be used
            

        #copy values from configuration to live value
        for processTagName in tagsToWriteList:
            try:    #watch out for wrongly given tags
                valueChanged = False
                
                #write value to internal memory - apply limits for real values
                if (self.__internalPDI[processTagName].valueType == VALUE_TYPE_REAL):
                    #get current live value: either from write list if given or from live value
                    if (tagsToWriteList[processTagName] == None):
                        processTagValue = float(getattr(self, self.__internalPDI[processTagName].processTag))
                    else:
                        processTagValue = float(tagsToWriteList[processTagName])
                        
                    #limit before writing it to internal memory
                    #check whether there were limits set in the configuration file -> if not set it to the current value so min/max has no effect
                    try:
                        highValue = float(self.__internalPDI[processTagName].highREAL)
                    except:
                        highValue = processTagValue
                        
                    try:
                        lowValue = float(self.__internalPDI[processTagName].lowREAL)
                    except:
                        lowValue = processTagValue
                    
                    processTagValue = max(min(float(processTagValue), highValue), lowValue)
                    #check whether value has been changed -> used for writing remanent data only when changed 
                    if (self.__internalPDI[processTagName].valueREAL != float(processTagValue)):
                        valueChanged = True
                    
                    #write limited value to internal memory
                    self.__internalPDI[processTagName].valueREAL = float(processTagValue)
                    #publish limited value through given tag list
                    tagsToWriteList[processTagName] = float(processTagValue)
                
                elif (self.__internalPDI[processTagName].valueType == VALUE_TYPE_TEXT):
                    #get current live value: either from write list if given or from live value
                    if (tagsToWriteList[processTagName] == None):
                        processTagValue = getattr(self, self.__internalPDI[processTagName].processTag)
                    else:
                        processTagValue = tagsToWriteList[processTagName]
    
                    #check whether value has been changed -> used for writing remanent data only when changed 
                    if (self.__internalPDI[processTagName].valueTEXT != processTagValue):
                        valueChanged = True
    
                    #write value to internal memory
                    self.__internalPDI[processTagName].valueTEXT = processTagValue
                    #publish limited value through given tag list
                    tagsToWriteList[processTagName] = processTagValue
                
                else:
                    print("Yaha_pdi write: process tag <{0}> value type {1} not supported".format(self.__internalPDI[processTagName].processTag, self.__internalPDI[processTagName].valueType))
                    
    
                #check if value is remanent
                if (self.__internalPDI[processTagName].isRemanent == REMANENT_TRUE) and (valueChanged == True):
                    try:
                        #open recipe file and read xml data
                        remXmlTree = xmlParser.parse(self.__internalRemDataFile)
                        remXmlRoot = remXmlTree.getroot()
                        #check whether element exists already in file
                        remXmlTag = remXmlRoot.find(processTagName)            
                        #if not existing, create node and append it
                        if (remXmlTag == None):
                            remXmlTag = xmlParser.Element(processTagName)
                            remXmlRoot.append(remXmlTag)
                        
                        #write new value into tag
                        remXmlTag.text = str(processTagValue)
                        remXmlTag.tail = "\n"
    
                        #as elementree would only write back pure data, recreate declaration node
                        xmlDeclaration = xmlParser.Element(None)                                    #create a dummy root element
                        pi = xmlParser.PI("xml", "version='1.0' encoding='UTF-8'")                  #add standard xml header
                        pi.tail = "\n"
                        xmlDeclaration.append(pi)
                        xmlDeclaration.append(remXmlRoot)                                              #add xml data to inserted elements
                        remXmlTree = xmlParser.ElementTree(xmlDeclaration)                             #load tree again with modified header
                        
                        #write modified values back to file
                        remXmlTree.write(self.__internalRemDataFile, xml_declaration=True)            #write tree to file
                    except Exception, e:
                        print('Saving remanent data failed: ' + str(e))
                        self.restoreRemanentDataXmlFile()
            
            except Exception, self.e:
                tagsToWriteList[processTagName] = ERROR_RESPONSE_TAG_UNKNOWN
                print("Yaha_pdi write: process tag <{0}> error: {1}".format(processTagName, self.e))
            
        
        return tagsToWriteList      #give back list with limited values


    def getTagDeviceIDs(self, owner):
        deviceIDlist = dict()
        for processTagName in self.__internalPDI:
            #check if owner string of PDI configuration starts with given owner
            if (self.__internalPDI[processTagName].owner.startswith(owner)):
                deviceIDlist[self.__internalPDI[processTagName].processTag] = self.__internalPDI[processTagName].deviceID   #"tag" : ID
        
        return(deviceIDlist)
                

    def getTagHostChannels(self, owner):
        channelList = dict()
        
        for processTagName in self.__internalPDI:
            #check if owner string of PDI configuration starts with given owner
            if (self.__internalPDI[processTagName].owner.startswith(owner)):
                try:
                    channelList[self.__internalPDI[processTagName].processTag] = self.__internalPDI[processTagName].owner.split('.')[1]   #"tag" : owner.01 => tag : 01 
                except:
                    channelList[self.__internalPDI[processTagName].processTag] = None   #no specific host ID defined => use base ID in driver later on
            
        return(channelList)
    

    def restoreRemanentDataXmlFile(self):
        #try to remove corrupt file
        try:
            os.remove(self.__internalRemDataFile)
        except:
            pass
        #create new file with empty xml
        try:
            with open(self.__internalRemDataFile, "w") as f:
                f.write("<?xml version='1.0' encoding='us-ascii'?><pdi></pdi>")                
        except Exception, e:
            print("Error creating new remanent data xml file: {0}".format(e))


        

class ProcessDataItem:
    "Holds information about one single data item"
    def __init__(self): 
        self.processTag = ""
        self.valueType = ""
        self.valueREAL = 0.0
        self.valueTEXT = ""
        self.domain = ""
        self.owner = ""
        self.deviceID = ""
        self.lowREAL = 0.0
        self.highREAL = 0.0
        self.zone = ""
        self.subzone = ""
        self.room = ""
        self.isRemanent = ""


#debugging
if __name__ == "__main__":
    print("!!! DEBUGGING of yaha_pdi active !!!")
    pdi = ProcessDataImage('/home/pi/Yaha/rem_data/rem_data.xml')
    pdi.addItemsFromFile('/home/pi/Yaha/modules/blinds_shading/module.pdi.xml')
    pdi.read()
    pdi.write()
