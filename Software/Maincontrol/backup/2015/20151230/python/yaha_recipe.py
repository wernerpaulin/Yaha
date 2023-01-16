#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as xmlParser
import os
import yaha_data
import json
import shutil

YAHA_RCP_SUFFIX = ".rcp.xml"
YAHA_RCP_DEFAULT_NAME = "yaha_pdi_default"

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
            print("Loading recipe failed")
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
        print("Recipe successfully loaded")
       
    def save(self, rcpName, isNew):
        if (rcpName == YAHA_RCP_DEFAULT_NAME):
            print("Default recipe is read only!")
            return

        self.currentProcessTagList = yaha_data.YahaGetProcessTagListWithValue()
        try:
            #open recipe file and read xml data
            self.rcpTree = xmlParser.parse(self.path + '/' + rcpName + YAHA_RCP_SUFFIX)
            self.rcpRoot = self.rcpTree.getroot()

            #go through all process tags and read necessary information for writing new values
            for self.tag in self.rcpRoot.findall('process_data'):
                self.processTag = self.tag.find('processTag').text
                self.valueType = self.tag.find('valueType').text
                self.valueREAL = self.tag.find('valueREAL').text
                self.valueTEXT = self.tag.find('valueTEXT').text

                #write value according to valueTYPE            
                if (self.valueType == "REAL"):
                    self.tag.find('valueREAL').text = str(self.currentProcessTagList[self.processTag])
                elif (self.valueType == "TEXT"):
                    self.tag.find('valueTEXT').text = str(self.currentProcessTagList[self.processTag])
                else:
                    print('Data type not supported: %s'%(self.valueType))
    
                #override currentRcpName in case this save is done by the create function -> set currentRcpName to new name
                if (self.processTag == "currentRcpName") and (isNew == True):
                    self.tag.find('valueTEXT').text = rcpName
                
            
            #As elementree would only write back pure data, recreate declaration node (e.g. xsl information for reading in browser 
            self.declaration = xmlParser.Element(None)                                      #create a dummy root element
            pi = xmlParser.PI("xml", "version='1.0' encoding='UTF-8'")                      #add standard xml header
            pi.tail = "\n"
            self.declaration.append(pi)
            pi = xmlParser.PI("xml-stylesheet", "type='text/xsl' href='yaha_pdi.xsl'")      #add PDI specific header
            pi.tail = "\n"
            self.declaration.append(pi)
            
            self.declaration.append(self.rcpRoot)                                           #add xml data to inserted elements
    
            self.rcpTree = xmlParser.ElementTree(self.declaration)                          #load tree again with modified header
            
            #write modified values back to file
            self.rcpTree.write(self.path + '/' + rcpName + YAHA_RCP_SUFFIX, xml_declaration=True)   #write tree to file

            print("Recipe successfully saved")
        except:
            print('Saving recipe failed')
            return

    def create(self, rcpName, functionPointer_PDIread):
        if (rcpName == YAHA_RCP_DEFAULT_NAME):
            print("Using name of default recipe is not allowed!")
            return
        else:
            try:
                shutil.copy (self.path + '/' + YAHA_RCP_DEFAULT_NAME + YAHA_RCP_SUFFIX, self.path + '/' + rcpName + YAHA_RCP_SUFFIX)
                self.save(rcpName, True)
                self.load(rcpName)
                functionPointer_PDIread()         #call PDI.load() to update live values with newest values from SQL DB written by self.load()
                print("Recipe successfully created")
            except:
                print("Error creating recipe file: %s", rcpName)
                return

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
                    #including full path self.rcpFileList.append(os.path.join(self.dirname, self.filename))
                    self.filename = self.filename[:self.filename.find(YAHA_RCP_SUFFIX)] #cur suffix
                    self.rcpFileList.append(self.filename)
                else:
                    continue
            break   #search only top directory (remove break to walk also all sub folders    
        
        return json.dumps(self.rcpFileList) #convert list into JSON format to be able to store it in data base as TEXT

    def loadHandler(self, cmdLoadRcp, rcpNameSelector, functionPointer_PDIread):
        if (cmdLoadRcp == 1):
            self.load(rcpNameSelector)
            functionPointer_PDIread()         #call PDI.load() to update live values with newest values from SQL DB written by self.load()
            cmdLoadRcp = 0
            
        return cmdLoadRcp

    def listHandler(self):
        return self.list()
 
    def saveHandler(self, cmdSaveRcp, rcpNameSelector):
        if (cmdSaveRcp == 1):
            self.save(rcpNameSelector, False)
            cmdSaveRcp = 0
        
       
        return cmdSaveRcp 

    def createHandler(self, cmdCreateRcp, newRcpName, functionPointer_PDIread):
        if (cmdCreateRcp == 1):
            self.create(newRcpName, functionPointer_PDIread)
            cmdCreateRcp = 0
            
        return cmdCreateRcp
 

