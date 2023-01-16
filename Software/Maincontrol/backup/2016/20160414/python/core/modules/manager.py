#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import os
import os.path
import sys

YAHA_MODULE_PDI_FILE_NAME = 'module.pdi.xml'
YAHA_MODULE_ROOT_PATH = '/home/pi/Yaha/modules'

class main():
    "Module manager"
    def __init__(self, PDI):
        self.PDI = PDI
        self.YahaModuleReferenceList = dict()
        self.YahaModuleRootPath = None
        
        #load all modules and initialize them
        self.createYahaModuleList(YAHA_MODULE_ROOT_PATH)
        self.initializeYahaModules()
        self.addPDIitemsFromModules()
        
    
    #imports all modules found and creates a module information structure    
    def createYahaModuleList(self, moduleRootPath):
        self.YahaModuleRootPath = moduleRootPath
        
        #go through all directories in module folder and dynamically import all module.py files as yaha modules
        for item in os.listdir(self.YahaModuleRootPath):
            path = os.path.join(self.YahaModuleRootPath, item)
            
            #ignore all files, just go for directories
            if os.path.isdir(path):
                pyPackageName = os.path.basename(item)
                pyModuleName = os.path.basename(item) + ".module"
                
                #set up module information structure and assign function pointers for later usage: "lights_switches" : yahaModuleInfo object
                self.YahaModuleReferenceList[pyPackageName] = yahaModuleInfo()
                self.YahaModuleReferenceList[pyPackageName].ModuleRef = __import__("modules.%s" % (pyModuleName), fromlist=["init", "update"])
                self.YahaModuleReferenceList[pyPackageName].InitFunctionRef = self.YahaModuleReferenceList[pyPackageName].ModuleRef.init
                self.YahaModuleReferenceList[pyPackageName].UpdateFunctionRef = self.YahaModuleReferenceList[pyPackageName].ModuleRef.update

    #calls all given init routines of all modules
    def initializeYahaModules(self):
        for module in self.YahaModuleReferenceList:
            try:
                self.YahaModuleReferenceList[module].InitFunctionRef(self.PDI)
            except Exception, self.e:
                print("Module manager: init function not defined: %s"%(self.e))

    #updates all modules
    def updateYahaModules(self):
        for module in self.YahaModuleReferenceList:
            try:
                self.YahaModuleReferenceList[module].UpdateFunctionRef(self.PDI)
            except Exception, self.e:
                print("Module manager: update function not defined: %s"%(self.e))

    def getPathListToPDI(self):
        pathList = []
        
        #go through all directories in module folder and watch out for PDI configuration files
        for item in os.listdir(self.YahaModuleRootPath):
            path = os.path.join(self.YahaModuleRootPath, item)

            #ignore all files, just go for directories
            if os.path.isdir(path):
                pathList.append(path + '/' + YAHA_MODULE_PDI_FILE_NAME)
        
        return pathList
    
    def addPDIitemsFromModules(self):
        pdiPathList = []
        
        pdiPathList = self.getPathListToPDI()
        for path in pdiPathList:
            #check if PDI configuration actually exists (modules do not need to have a PDI configuration
            if (os.path.isfile(path) == True):
                self.PDI.addItemsFromFile(path)        
            else:
                continue
        
        return

class yahaModuleInfo():
    "Contains all information for a certain Yaha module"
    def __init__(self):
        self.ModuleRef = None
        self.InitFunctionRef = None
        self.UpdateFunctionRef = None
        
    