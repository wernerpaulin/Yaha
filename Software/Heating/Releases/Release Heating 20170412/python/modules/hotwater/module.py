#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import math

import core.modules.iosignal
import core.modules.filter


MODULE_CFG_FILE_NAME = "module.cfg.xml"
BOILER_CFG_ELEMENT_NAME = "./boilers/boiler"
PROCESSTAG_ELEMENT_NAME = "processtag"

AUTOMATIC_MODE = 0
MANUAL_MODE = 1
SIMULATION_ON = 1
HOTWATER_PREPARATION_INACTIVE = 0
HOTWATER_PREPARATION_ACTIVE = 1

SUNDAY_INDEX = 6

def init(PDI):
    global Boilers
    Boilers = dict()
    attrList = [] 
    boilerID = None



    #read module configuration and initialize each boiler
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for boilerCfg in cfgRoot.findall(BOILER_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                boilerID = boilerCfg.get('id')
                Boilers[boilerID] = boilerManager(PDI)
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Boilers[boilerID].inputs)      #['burnerActTemp', 'burnerSetTemp',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="switchedOn">
                    inputCfg = boilerCfg.find('.//inputs/input[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Boilers[boilerID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(Boilers[boilerID].outputs)      #['pumpRelease',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = boilerCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Boilers[boilerID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)


                #initialize settings parameter
                settingsNameList = getClassAttributes(Boilers[boilerID].param.settings)      #['hysteresisHigh', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = boilerCfg.find('.//parameters/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Boilers[boilerID].param.settings, settingName, float(settingCfg.text))
                
                #initialize operating modes parameter
                #switch
                operatingSwitchCfg = boilerCfg.find('.//parameters/operatingmodes/switch')
                if operatingSwitchCfg != None:                
                    #get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
                    processTagList = operatingSwitchCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                    #add processTags to IO signal
                    for processTag in processTagList:
                        #convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
                        attrList = []
                        for attr in processTag.attrib:
                            attrList.append(processTag.attrib[attr])
    
                        #each IOsignal has an addProcessTag function: call it generically depending on ioName
                        ioSignalInst = getattr(Boilers[boilerID].param.operatingModes, "switch")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                
                
                #modes
                operatingModeNameList = getClassAttributes(Boilers[boilerID].param.operatingModes.modes)      #['automatic', ...]
                #try to find the corresponding entry in the configuration file 
                for operatingModeName in operatingModeNameList:
                    operatingModeCfg = boilerCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]')
                    #continue only if configuration exists
                    if operatingModeCfg != None:
                        #access operating mode infrastructure and initialize interfaces
                        operatingModeObj = getattr(Boilers[boilerID].param.operatingModes.modes, operatingModeName)
                        interfaceNameList = getClassAttributes(operatingModeObj)      #['setTemperature', ...]
                        #try to find settings for all found interfaces
                        for interfaceName in interfaceNameList:
                            interfaceCfg = boilerCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]' + '/interfaces/interface[@name="' + interfaceName + '"]')
                            #continue only if configuration exists
                            if interfaceCfg != None:                
                                #get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
                                processTagList = interfaceCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                                #add processTags to IO signal
                                for processTag in processTagList:
                                    #convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
                                    attrList = []
                                    for attr in processTag.attrib:
                                        attrList.append(processTag.attrib[attr])
                
                                    #each IOsignal has an addProcessTag function: call it generically depending on ioName
                                    ioSignalInst = getattr(operatingModeObj, interfaceName)              #get access to IO signal: "up", "down",...
                                    ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize simulation parameter
                #enable
                simulationEnableCfg = boilerCfg.find('.//parameters/simulation/enable')
                if simulationEnableCfg != None:                
                    #get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
                    processTagList = simulationEnableCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                    #add processTags to IO signal
                    for processTag in processTagList:
                        #convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
                        attrList = []
                        for attr in processTag.attrib:
                            attrList.append(processTag.attrib[attr])
    
                        #each IOsignal has an addProcessTag function: call it generically depending on ioName
                        ioSignalInst = getattr(Boilers[boilerID].param.simulation, "enable")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                                

                #settings
                settingsNameList = getClassAttributes(Boilers[boilerID].param.simulation.settings)      #['burnerTemperaturePtTau', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = boilerCfg.find('.//parameters/simulation/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Boilers[boilerID].param.simulation.settings, settingName, float(settingCfg.text))


                #initialize status points
                ioNameList = getClassAttributes(Boilers[boilerID].status)      #['state', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    statusCfg = boilerCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Boilers[boilerID].status, ioName)              #get access to IO signal: "state", "setTemperature",...
                            ioSignalInst.addProcessTag(processTag.text, None)

            except Exception as e:
                print("Loading configuration for boiler <{0}> failed: {1}".format(boilerID, e))
                return    

    except Exception as e:
        print("Loading boilers module configuration <{0}> failed: {1}".format(boilerID, e))
        return    





def update(PDI):
    global Boilers
    '''
    Functional description    

    '''
    for boiler in Boilers:
        Boilers[boiler].update(PDI)


class boilerManager:
    "Control of boilers"
    #init
    def __init__(self, PDI):
        self.inputs = boilerInputs(PDI)
        self.outputs = boilerOutputs(PDI)
        self.param = boilerParameters(PDI)
        self.status = boilerStatus(PDI)
        self.currentYear = datetime.datetime.now().year

        self.hotwaterPreparationRelease = False
        
        self.legionellaProtectionDone = False
        self.legionellaProtectionStartTimer = 0
        
        self.simTemperaturePT2 = core.modules.filter.PT2()

        self.lastCallTime = time.time()
        self.samplingTime = 0
        
        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sAUTOMATIC": self.sAUTOMATIC,
                             "sMANUAL": self.sMANUAL
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""


    #cyclic logic    
    def update(self, PDI):
        #cycle time calculation
        self.samplingTime = max(time.time() - self.lastCallTime, 0)
        self.lastCallTime = time.time()

        #execute state machine
        self.statemachine[self.activeState]()
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Boiler state: " + self.activeState)

        #simulation
        if (self.param.simulation.enable.value() == SIMULATION_ON):
            self.simulationLogic()

    def sIDLE(self):
        if (self.param.operatingModes.switch.value() == AUTOMATIC_MODE):
            self.activeState = "sAUTOMATIC"
        elif (self.param.operatingModes.switch.value() == MANUAL_MODE):
            self.activeState = "sMANUAL"
        
    def sAUTOMATIC(self):
        #leave automatic mode in case of new mode
        if (self.param.operatingModes.switch.value() != AUTOMATIC_MODE):
            self.activeState = "sIDLE"
            return
        
        #check whether a hotwater phase is now scheduled
        self.currentTimeMidnightMinutes = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute #current minutes since midnight
        self.hotwaterPreparationRelease = False
        
        #morning phase
        try:
            #convert start and end time string into a time object
            startTime = time.strptime(self.param.operatingModes.modes.automatic.morningStartTime.value(), '%H:%M')
            endTime = time.strptime(self.param.operatingModes.modes.automatic.morningEndTime.value(), '%H:%M')
            
            #remove date information of current time because comparison would fail as start and end time have no date
            currentTimeString = str(datetime.datetime.today().hour) + ":" + str(datetime.datetime.today().minute)
            currentTime = time.strptime(currentTimeString, '%H:%M')
            
            #check whether current time is within heating phase
            if (startTime <= currentTime <= endTime):
                #within hotwater phase release preparation
                self.hotwaterPreparationRelease = True
            else:
                #outside heating phase set temperature is reduced temperature
                self.hotwaterPreparationRelease = False

        except Exception as e:
            print("Boiler morning phase configuration error: {0}".format(e))
            self.hotwaterPreparationRelease = False


        #evening phase (ignore this check if it is already clear the hotwater preparation is already release (in case user only configures only one phase (morning phase)
        if (self.hotwaterPreparationRelease == False):
            try:
                #convert start and end time string into a time object
                startTime = time.strptime(self.param.operatingModes.modes.automatic.eveningStartTime.value(), '%H:%M')
                endTime = time.strptime(self.param.operatingModes.modes.automatic.eveningEndTime.value(), '%H:%M')
                
                #remove date information of current time because comparison would fail as start and end time have no date
                currentTimeString = str(datetime.datetime.today().hour) + ":" + str(datetime.datetime.today().minute)
                currentTime = time.strptime(currentTimeString, '%H:%M')
                
                #check whether current time is within heating phase
                if (startTime <= currentTime <= endTime):
                    #within hotwater phase release preparation
                    self.hotwaterPreparationRelease = True
                else:
                    #outside heating phase set temperature is reduced temperature
                    self.hotwaterPreparationRelease = False
                    
            except Exception as e:
                print("Boiler evening phase configuration error: {0}".format(e))
                self.hotwaterPreparationRelease = False
    
        #in case hotwater should be prepared start 2-point controller
        if (self.hotwaterPreparationRelease == True):
            self.status.state.value(HOTWATER_PREPARATION_ACTIVE)
            #On sunday higher set temperature to kill legionella until a certain time with high temperature has been elapsed  
            if (datetime.datetime.today().weekday() == SUNDAY_INDEX) and (self.legionellaProtectionDone == False):
                self.status.setTemperature.value(self.param.settings.legionellaProtectionTemperature)
            else:
                self.status.setTemperature.value(self.param.operatingModes.modes.automatic.setTemperature.value())
            
            #reset done flag once Sunday is over
            if (datetime.datetime.today().weekday() != SUNDAY_INDEX):
                self.legionellaProtectionDone = False
                self.legionellaProtectionStartTimer = 0
                
            #two point controller
            if (self.inputs.hotwaterActTemp.value() < self.status.setTemperature.value() - self.param.settings.hysteresisLow):
                self.outputs.burnerSetTemp.value(self.status.setTemperature.value() + self.param.settings.burnerSetTempOffset)
                #switch on pump only if burner is warmer than current hot water
                if (self.inputs.burnerActTemp.value() > self.inputs.hotwaterActTemp.value()):
                    self.outputs.pumpRelease.value(1)
                else:
                    self.outputs.pumpRelease.value(0)

            if (self.inputs.hotwaterActTemp.value() > self.status.setTemperature.value() + self.param.settings.hysteresisHigh):
                self.outputs.burnerSetTemp.value(0.0)
                self.outputs.pumpRelease.value(0)
        else:
            self.status.state.value(HOTWATER_PREPARATION_INACTIVE)
            self.status.setTemperature.value(0.0)
            self.outputs.burnerSetTemp.value(0.0)
            self.outputs.pumpRelease.value(0)

        #to kill legionella bacterias it is not necessary to stay at high temperature for an entire day 
        if (self.inputs.hotwaterActTemp.value() >= self.param.settings.legionellaProtectionTemperature):
            self.legionellaProtectionStartTimer = self.legionellaProtectionStartTimer + self.samplingTime

            if (self.legionellaProtectionStartTimer > self.param.settings.legionellaProtectionHeatDuration):
                self.legionellaProtectionDone = True
        else:
            self.legionellaProtectionStartTimer = 0

    def sMANUAL(self):
        #leave manual mode in case of new mode
        if (self.param.operatingModes.switch.value() != MANUAL_MODE):
            self.activeState = "sIDLE"
            return

    def simulationLogic(self):
        #simulate temperature behavior
        if (self.inputs.ioPumpRelease.value() == 1):
            self.simTargetTemp = self.inputs.burnerActTemp.value()
        else:
            self.simTargetTemp = self.param.simulation.settings.environmentalTemperature
        
        self.inputs.hotwaterActTemp.value(self.simTemperaturePT2.update(self.simTargetTemp, self.param.simulation.settings.boilerTemperaturePtTau, 1))
        self.inputs.hotwaterActTemp.value(max(self.inputs.hotwaterActTemp.value(), self.param.simulation.settings.environmentalTemperature))


class boilerInputs():
    'Collection of inputs of a certain boiler'
    #init
    def __init__(self, PDI):
        self.burnerActTemp = core.modules.iosignal.IOsignal(PDI)
        self.hotwaterActTemp = core.modules.iosignal.IOsignal(PDI)
        self.ioPumpRelease = core.modules.iosignal.IOsignal(PDI)

class boilerOutputs():
    'Collection of outputs of a certain boiler'
    #init
    def __init__(self, PDI):
        self.burnerSetTemp = core.modules.iosignal.IOsignal(PDI)
        self.pumpRelease = core.modules.iosignal.IOsignal(PDI)


class boilerParameters:
    #init
    def __init__(self, PDI):
        self.settings = paramSettings()
        self.operatingModes = paramOperatingModes(PDI)
        self.simulation = paramSimulation(PDI)

class paramSettings:
    #init
    def __init__(self):
        self.hysteresisHigh = 0.0
        self.hysteresisLow = 0.0
        self.legionellaProtectionTemperature = 0.0
        self.legionellaProtectionHeatDuration = 0.0
        self.burnerSetTempOffset = 0.0

class paramOperatingModes:
    #init
    def __init__(self, PDI):
        self.switch = core.modules.iosignal.IOsignal(PDI)
        self.modes = paramOperatingModesTypes(PDI)

class paramOperatingModesTypes:
    #init
    def __init__(self, PDI):
        self.automatic = interfaceAutomaticMode(PDI)
    

class paramSimulation:
    #init
    def __init__(self, PDI):
        self.enable = core.modules.iosignal.IOsignal(PDI);
        self.settings = paramSimulationSettings()

class paramSimulationSettings:
    #init
    def __init__(self):
        self.boilerTemperaturePtTau = 0.0
        self.environmentalTemperature = 0.0


class interfaceAutomaticMode:
    #init
    def __init__(self, PDI):
        self.setTemperature = core.modules.iosignal.IOsignal(PDI);
        self.morningStartTime = core.modules.iosignal.IOsignal(PDI);
        self.morningEndTime = core.modules.iosignal.IOsignal(PDI);
        self.eveningStartTime = core.modules.iosignal.IOsignal(PDI);
        self.eveningEndTime = core.modules.iosignal.IOsignal(PDI);


class boilerStatus:
    #init
    def __init__(self, PDI):
        self.state = core.modules.iosignal.IOsignal(PDI);
        self.setTemperature = core.modules.iosignal.IOsignal(PDI);


#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    
