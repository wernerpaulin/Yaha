#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as xmlParser
import os
import yaha_data

YAHA_RCP_SUFFIX = ".rcp.xml"

class Manager:
    'Yaha recipe manager: loads and saves recipe data to xml files'

    def __init__(self, path):
        self.path = path

    def load(self, rcpName):
        #reads recipe data from xml file and 
        self.rcpData = {'empty': 0}    #force creating a dictionary
        self.rcpData.clear()           #clear dictionary immediately

        try:
            self.rcpTree = xmlParser.parse(self.path + '/' + rcpName + YAHA_RCP_SUFFIX)
            self.rcpRoot = self.rcpTree.getroot()
        except:
            return
        
        #walk through all process data elements in recipe
        for self.rcpTag in self.rcpRoot:
            self.tagName, self.tagValue, self.tagValueType = 0,0,0     #avoid any old value from previous record in case an element is not given

            #read out all relevant properties (= sub children) into a dictionary
            for self.property in self.rcpTag:
                if (self.property.tag == 'processTag'):
                    self.tagName = self.property.text
                elif (self.property.tag == 'valueType'):
                    self.tagValueType = self.property.text

            #xml is per default text. In case a real value has been read force conversion to real
            for self.property in self.rcpTag:
                if (self.property.tag == 'valueREAL') and (self.tagValueType == 'REAL'):
                        try:
                            self.tagValue = float(self.property.text)
                        except:
                            print('Value can not be concerted to float: %s'%(self.property.text))                

                elif (self.property.tag == 'valueTEXT') and (self.tagValueType == 'TEXT'):
                        self.tagValue = self.property.text
                    
            self.rcpData[self.tagName] = self.tagValue     #build dictionary (e.g.: setTempFelix: 11.0)

        yaha_data.YahaPDIwriteValue(self.rcpData, {})       #write process tags
        
    def save(self, rcpName):
        print("Rcp save")
        #1. SQL-DB in XML umwandeln
        #2. xmlParser.tostring(self.xmlDoc, encoding="utf-8", method="xml")

    #get list of recipe files in a certain directory: *.rcp, *.rcp.xml
    def list(self):
        self.rcpFileList = []
        for self.dirname, self.dirnames, self.filenames in os.walk(self.path):
            #dirname: current directory
            #dirnames: directories in current directory
            #filenames: file in current directory
            for self.filename in self.filenames:
                #get extension of file
                if (self.filename.split('.')[1] == 'rcp'):
                    #add all receipe 
                    self.rcpFileList.append(os.path.join(self.dirname, self.filename))
                else:
                    continue
            break   #search only top directory (remove break to walk also all sub folders    
        
        return self.rcpFileList

    def loadHandler(self, cmdLoadRcp, rcpNameSelector):
        if (cmdLoadRcp == 1):
            self.load(rcpNameSelector)
            cmdLoadRcp = 0
            
        return cmdLoadRcp 
 
    def saveHandler(self, cmdSaveRcp, rcpNameSelector):
        if (cmdSaveRcp == 1):
            self.load(rcpNameSelector)
            cmdSaveRcp = 0
        
        print("weiter machen: saveHandler")
        #1. SQL-DB in XML umwandeln
        #2. xmlParser.tostring(self.xmlDoc, encoding="utf-8", method="xml")
       
        return cmdSaveRcp 

    def createHandler(self, cmdCreateRcp, newRcpName):
        if (cmdCreateRcp == 1):
            self.load(newRcpName)
            cmdCreateRcp = 0
            
        return cmdCreateRcp, newRcpName
 

