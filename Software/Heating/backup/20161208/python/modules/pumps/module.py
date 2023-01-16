#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time

import core.modules.iosignal

MODULE_CFG_FILE_NAME = "module.cfg.xml"
PUMP_CFG_ELEMENT_NAME = "./pumps/pump"
PROCESSTAG_ELEMENT_NAME = "processtag"

AUTOMATIC_MODE = 0
MANUAL_MODE = 1
SIMULATION_ON = 1

def init(PDI):
    global Pumps
    Pumps = dict()
    attrList = [] 
    pumpID = None



    #read module configuration and initialize each burner
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for pumpCfg in cfgRoot.findall(PUMP_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                pumpID = pumpCfg.get('id')
                Pumps[pumpID] = pumpManager(PDI)
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Pumps[pumpID].inputs)      #['safetyRelease', 'switchedOn',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="switchedOn">
                    inputCfg = pumpCfg.find('.//inputs/input[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Pumps[pumpID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(Pumps[pumpID].outputs)      #['release',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = pumpCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Pumps[pumpID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)


                #initialize settings parameter
                settingsNameList = getClassAttributes(Pumps[pumpID].param.settings)      #['frostProtectTemperature', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = pumpCfg.find('.//parameters/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Pumps[pumpID].param.settings, settingName, float(settingCfg.text))
                
                #initialize operating modes parameter
                #switch
                operatingSwitchCfg = pumpCfg.find('.//parameters/operatingmodes/switch')
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
                        ioSignalInst = getattr(Pumps[pumpID].param.operatingModes, "switch")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                
                
                #modes
                operatingModeNameList = getClassAttributes(Pumps[pumpID].param.operatingModes.modes)      #['automatic', ...]
                #try to find the corresponding entry in the configuration file 
                for operatingModeName in operatingModeNameList:
                    operatingModeCfg = pumpCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]')
                    #continue only if configuration exists
                    if operatingModeCfg != None:
                        #access operating mode infrastructure and initialize interfaces
                        operatingModeObj = getattr(Pumps[pumpID].param.operatingModes.modes, operatingModeName)
                        interfaceNameList = getClassAttributes(operatingModeObj)      #['setTemperature', ...]
                        #try to find settings for all found interfaces
                        for interfaceName in interfaceNameList:
                            interfaceCfg = pumpCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]' + '/interfaces/interface[@name="' + interfaceName + '"]')
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
                simulationEnableCfg = pumpCfg.find('.//parameters/simulation/enable')
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
                        ioSignalInst = getattr(Pumps[pumpID].param.simulation, "enable")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                                

                #initialize status points
                ioNameList = getClassAttributes(Pumps[pumpID].status)      #['state', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    statusCfg = pumpCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Pumps[pumpID].status, ioName)              #get access to IO signal: "state", "setTemperature",...
                            ioSignalInst.addProcessTag(processTag.text, None)

            except Exception as e:
                print("Loading configuration for pump <{0}> failed: {1}".format(pumpID, e))
                return    

    except Exception as e:
        print("Loading pumps module configuration <{0}> failed: {1}".format(pumpID, e))
        return    



def update(PDI):
    global Pumps
    '''
    Functional description    
    automatic/manual mode
    statistical counters
    frost protection
    optional safety release monitoring
    '''
    for pump in Pumps:
        Pumps[pump].update(PDI)



class pumpManager:
    "Control of pumps"
    #init
    def __init__(self, PDI):
        self.inputs = pumpInputs(PDI)
        self.outputs = pumpOutputs(PDI)
        self.param = pumpParameters(PDI)
        self.status = pumpStatus(PDI)
        self.currentYear = datetime.datetime.now().year
        self.oldHour = datetime.datetime.now().hour
        self.oldMinute = datetime.datetime.now().minute
        self.cntMinutesSwitchedOn = 0
        
        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sAUTOMATIC": self.sAUTOMATIC,
                             "sMANUAL": self.sMANUAL
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""
        self.startTimeRelease = 0

    #cyclic logic    
    def update(self, PDI):
        #alarm handling
        #pump is switched on but safety release is not yet on -> monitor time
        try:        #optional feature
            if (self.status.state.value() == 1) and (self.inputs.safetyRelease.value() == 0):
                if ((time.time() - self.startTimeRelease) > self.param.settings.safetyReleaseOnMaxDelay):
                    self.status.alarmSafetyReleaseOff.value(1)
            else:
                self.status.alarmSafetyReleaseOff.value(0)
        except:
            pass


        #execute state machine
        self.statemachine[self.activeState]()
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Pump state: " + self.activeState)
        
        #simulation
        if (self.param.simulation.enable.value() == SIMULATION_ON):
            self.simulationLogic()    

        #status building
        if (self.outputs.release.value() == 1):
            self.status.state.value(1)
        else:
            self.status.state.value(0)
            self.startTimeRelease = time.time()    #updating will be stopped when release

        #log pump activation duration with a 1-minute resolution
        if (self.oldMinute != datetime.datetime.now().minute):
            self.oldMinute = datetime.datetime.now().minute
            if (self.outputs.release.value() == 1):
                self.cntMinutesSwitchedOn = self.cntMinutesSwitchedOn + 1 

        #statistics: update PDI variables only every our to avoid too many file writes because these are remanent data
        if (self.oldHour != datetime.datetime.now().hour):
            self.oldHour = datetime.datetime.now().hour
            self.status.annualOperatingHours.value(self.status.annualOperatingHours.value() + float(self.cntMinutesSwitchedOn) / 60)
            self.status.totalOperatingHours.value(self.status.totalOperatingHours.value() + float(self.cntMinutesSwitchedOn) / 60)
            self.cntMinutesSwitchedOn = 0
  
        #reset annual operating hour counter in case of a new year
        if (self.currentYear != datetime.datetime.now().year):
            self.status.annualOperatingHours = 0
            self.currentYear = datetime.datetime.now().year
        


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
        
        #optional: frost protection
        try:
            if (self.inputs.pipeAmbientTemperature.value() <= self.param.settings.frostProtectTemperature):
                self.outputs.release.value(1)   #always on if pipe is exposed to low temperatures
                self.status.alarmFrostProtectionActive.value(1)
            else:
                #control pump directly with input from other sources
                self.outputs.release.value(self.inputs.release.value())
                self.status.alarmFrostProtectionActive.value(0)
        except:
            #control pump directly with input from other sources
            self.outputs.release.value(self.inputs.release.value())
            

    def sMANUAL(self):
        #leave manual mode in case of new mode
        if (self.param.operatingModes.switch.value() != MANUAL_MODE):
            self.outputs.release.value(0)
            self.activeState = "sIDLE"
            return

        #control pump directly with user input
        self.outputs.release.value(self.param.operatingModes.modes.manual.release.value())


    def simulationLogic(self):
        #bypass safety check in simulation: on as soon as pump is on + no alarm
        try:
            self.inputs.safetyRelease.value(self.outputs.release.value())
        except:
            pass


class pumpInputs():
    'Collection of inputs of a certain pump'
    #init
    def __init__(self, PDI):
        self.release = core.modules.iosignal.IOsignal(PDI)
        self.pipeAmbientTemperature = core.modules.iosignal.IOsignal(PDI)
        self.safetyRelease = core.modules.iosignal.IOsignal(PDI)

class pumpOutputs():
    'Collection of outputs of a certain pump'
    #init
    def __init__(self, PDI):
        self.release = core.modules.iosignal.IOsignal(PDI)


class pumpParameters:
    #init
    def __init__(self, PDI):
        self.settings = paramSettings()
        self.operatingModes = paramOperatingModes(PDI)
        self.simulation = paramSimulation(PDI)

class paramSettings:
    #init
    def __init__(self):
        self.frostProtectTemperature = None     #optional: if not configured it remains none
        self.safetyReleaseOnMaxDelay = None     #optional: if not configured it remains none

class paramOperatingModes:
    #init
    def __init__(self, PDI):
        self.switch = core.modules.iosignal.IOsignal(PDI)
        self.modes = paramOperatingModesTypes(PDI)

class paramOperatingModesTypes:
    #init
    def __init__(self, PDI):
        self.automatic = interfaceAutomaticMode(PDI)
        self.manual = interfaceManualMode(PDI)

class paramSimulation:
    #init
    def __init__(self, PDI):
        self.enable = core.modules.iosignal.IOsignal(PDI);
    
class interfaceAutomaticMode:
    #init
    def __init__(self, PDI):
        self.release = core.modules.iosignal.IOsignal(PDI);

class interfaceManualMode:
    #init
    def __init__(self, PDI):
        self.release = core.modules.iosignal.IOsignal(PDI);


class pumpStatus:
    #init
    def __init__(self, PDI):
        self.state = core.modules.iosignal.IOsignal(PDI);
        self.totalOperatingHours = core.modules.iosignal.IOsignal(PDI);
        self.annualOperatingHours = core.modules.iosignal.IOsignal(PDI);
        self.alarmFrostProtectionActive = core.modules.iosignal.IOsignal(PDI);
        self.alarmSafetyReleaseOff = core.modules.iosignal.IOsignal(PDI);


#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]