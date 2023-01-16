#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import os
import os.path
import sys

class main():
    "Module manager"
    def __init__(self, PDI):
        self.PDI = PDI
        self.YahaModuleReferenceList = dict()
    
    #imports all modules found and creates a module information structure    
    def createYahaModuleList(self, moduleRootPath):
        #go through all directories in module folder and dynamically import all module.py files as yaha modules
        for item in os.listdir(moduleRootPath):
            path = os.path.join(moduleRootPath, item)
            
            #ignore all files, just go for directories
            if os.path.isdir(path):
                pyPackageName = os.path.basename(item)
                pyModuleName = os.path.basename(item) + ".module"
                
                #set up module information structure and assign function pointers for later usage
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
            except:
                print("Module manager: update function not defined: %s"%(self.e))


class yahaModuleInfo():
    "Contains all information for a certain Yaha module"
    def __init__(self):
        self.ModuleRef = None
        self.InitFunctionRef = None
        self.UpdateFunctionRef = None
        
    