#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import xycurvelin

import core.modules.iosignal
from core.modules.cal_event import *

MODULE_CFG_FILE_NAME = "module.cfg.xml"
LIN_CURVE_CFG_ELEMENT_NAME = "./sensors/linearizationcurves/linearizationcurve"
SENSOR_CFG_ELEMENT_NAME = "./sensors/sensor"
PROCESSTAG_ELEMENT_NAME = "processtag"


def init(PDI):
    global LinCurves
    global Sensors
    LinCurves = dict()
    Sensors = dict()
    attrList = []  


    #read module configuration and initialize each device
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()


        #read configuration of linearization curves
        for linCurveCfg in cfgRoot.findall(LIN_CURVE_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                curveID = linCurveCfg.get('id')
                LinCurves[curveID] = linearizationWrapper(PDI)
                LinCurves[curveID].curveID = curveID


                #initialize window parameter
                pointPairCfg = linCurveCfg.findall('.//pointpairs/pointpair')
                for pointPair in pointPairCfg:
                    LinCurves[curveID].curveData.addPointPair(float(pointPair.attrib['x']), float(pointPair.attrib['y']))        

            except Exception as e:
                print("Loading configuration for curve <{0}> failed: {1}".format(curveID, e))
                return    
            
        #read configuration of sensors
        for sensorCfg in cfgRoot.findall(SENSOR_CFG_ELEMENT_NAME):
            try:
                sensorID = sensorCfg.get('id')
                Sensors[sensorID] = sensorWrapper(PDI)
                Sensors[sensorID].sensorID = sensorID
                Sensors[sensorID].linCurve = LinCurves[sensorCfg.get('linearizationcurveid')]
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Sensors[sensorID].inputs)
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="on">
                    inputCfg = sensorCfg.find('.//inputs/input[@name="' + ioName + '"]')
                    if inputCfg != None:
                        #get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
                        processTagList = inputCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
                            attrList = []
                            for attr in processTag.attrib:
                                attrList.append(processTag.attrib[attr])
        
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Sensors[sensorID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)
        
                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(Sensors[sensorID].outputs)      #['open', 'close', 'teach']
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = sensorCfg.find('.//outputs/output[@name="' + ioName + '"]')
                    if outputCfg != None:
                        #get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
                        processTagList = outputCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
                            attrList = []
                            for attr in processTag.attrib:
                                attrList.append(processTag.attrib[attr])
        
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Sensors[sensorID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)


                
            except Exception as e:
                print("Loading configuration for sensor <{0}> failed: {1}".format(sensorID, e))
                return    

    except Exception as e:
        print("Loading module configuration <{0}> for heating control: {1}".format(MODULE_CFG_FILE_NAME,e))
        return



def update(PDI):
    global LinCurves

    #handle all sensors
    for sensor in Sensors:
        Sensors[sensor].update(PDI)


class linearizationWrapper:
    "Does the linearization and conversion of all temperature sensors"
   
    #init
    def __init__(self, PDI):
        self.curveID = None
        self.curveData = xycurvelin.chartLin()


class sensorWrapper:
    "Handles raw value conversion of sensors"
    
    #init
    def __init__(self, PDI):
        self.sensorID = None
        self.linCurve = None
        self.inputs = sensorInputs(PDI)
        self.outputs = sensorOutputs(PDI)

    #cyclic raw value conversion    
    def update(self, PDI):
        self.outputs.scaledvalue.value(self.linCurve.curveData.calcYfromX(self.inputs.rawvalue.value()))

        
class sensorInputs:
    "Inputs of sensor"

    #init
    def __init__(self, PDI):
        self.rawvalue = core.modules.iosignal.IOsignal(PDI)
        
class sensorOutputs:
    "Outputs of sensor"

    #init
    def __init__(self, PDI):
        self.scaledvalue = core.modules.iosignal.IOsignal(PDI)        
        
        
        
        
#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
        