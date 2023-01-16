#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py

import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import math

import core.modules.iosignal

MODULE_CFG_FILE_NAME = "module.cfg.xml"
BURNER_CFG_ELEMENT_NAME = "./burners/burner"
PROCESSTAG_ELEMENT_NAME = "processtag"

AUTOMATIC_MODE = 0
MANUAL_MODE = 1
SIMULATION_ON = 1

def init(PDI):
    global Burners
    Burners = dict()
    attrList = [] 
    burnerID = None



    #read module configuration and initialize each burner
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for burnerCfg in cfgRoot.findall(BURNER_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                burnerID = burnerCfg.get('id')
                Burners[burnerID] = burnerManager(PDI)
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Burners[burnerID].inputs)      #['actTemp', 'switchedOn',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="switchedOn">
                    inputCfg = burnerCfg.find('.//inputs/input[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Burners[burnerID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(Burners[burnerID].outputs)      #['release',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = burnerCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Burners[burnerID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)


                #initialize settings parameter
                settingsNameList = getClassAttributes(Burners[burnerID].param.settings)      #['maximumTemperature', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = burnerCfg.find('.//parameters/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Burners[burnerID].param.settings, settingName, float(settingCfg.text))
                
                #initialize operating modes parameter
                #switch
                operatingSwitchCfg = burnerCfg.find('.//parameters/operatingmodes/switch')
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
                        ioSignalInst = getattr(Burners[burnerID].param.operatingModes, "switch")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                
                
                #modes
                operatingModeNameList = getClassAttributes(Burners[burnerID].param.operatingModes.modes)      #['automatic', ...]
                #try to find the corresponding entry in the configuration file 
                for operatingModeName in operatingModeNameList:
                    operatingModeCfg = burnerCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]')
                    #continue only if configuration exists
                    if operatingModeCfg != None:
                        #access operating mode infrastructure and initialize interfaces
                        operatingModeObj = getattr(Burners[burnerID].param.operatingModes.modes, operatingModeName)
                        interfaceNameList = getClassAttributes(operatingModeObj)      #['setTemperature', ...]
                        #try to find settings for all found interfaces
                        for interfaceName in interfaceNameList:
                            interfaceCfg = burnerCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]' + '/interfaces/interface[@name="' + interfaceName + '"]')
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
                simulationEnableCfg = burnerCfg.find('.//parameters/simulation/enable')
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
                        ioSignalInst = getattr(Burners[burnerID].param.simulation, "enable")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                                

                #settings
                settingsNameList = getClassAttributes(Burners[burnerID].param.simulation.settings)      #['burnerTemperaturePtTau', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = burnerCfg.find('.//parameters/simulation/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Burners[burnerID].param.simulation.settings, settingName, float(settingCfg.text))


                #initialize status points
                ioNameList = getClassAttributes(Burners[burnerID].status)      #['state', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    statusCfg = burnerCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Burners[burnerID].status, ioName)              #get access to IO signal: "state", "setTemperature",...
                            ioSignalInst.addProcessTag(processTag.text, None)

            except Exception as e:
                print("Loading configuration for burner <{0}> failed: {1}".format(burnerID, e))
                return    

    except Exception as e:
        print("Loading burners module configuration <{0}> failed: {1}".format(burnerID, e))
        return    


def update(PDI):
    global Burners
    '''
    Functional description    
    automatic/manual mode
    statistical counters
    ensured minimum runtime 
    2-point controller with hysteresis
    full simulation of thermal behaviour
    '''
    for burner in Burners:
        Burners[burner].update(PDI)

class burnerManager:
    "Control of burners"
    #init
    def __init__(self, PDI):
        self.inputs = burnerInputs(PDI)
        self.outputs = burnerOutputs(PDI)
        self.param = burnerParameters(PDI)
        self.status = burnerStatus(PDI)
        self.currentYear = datetime.datetime.now().year
        self.currentDay = datetime.datetime.now().day
        self.oldHour = datetime.datetime.now().hour
        self.oldMinute = datetime.datetime.now().minute
        self.cntMinutesSwitchedOn = 0

        self.simTargetTemp = 0
        self.lastCallTime = time.time()
        self.samplingTime = 0
        
        self.switchedOnDuration = 0
        
        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sAUTOMATIC": self.sAUTOMATIC,
                             "sMANUAL": self.sMANUAL,
                             "sSTOP": self.sSTOP
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""


    #cyclic logic    
    def update(self, PDI):
        #cycle time calculation
        self.samplingTime = max(time.time() - self.lastCallTime, 0)
        self.lastCallTime = time.time()
        
        #alarm handling
        if (self.inputs.generalFailure.value() == 1):
            self.status.alarmGeneralFailure.value(1)
            self.activeState = "sSTOP"      #force entering stop state
        else:
            self.status.alarmGeneralFailure.value(0)

        if (self.inputs.overTemperature.value() == 1):
            self.status.alarmOvertemperature.value(1)
            self.activeState = "sSTOP"      #force entering stop state
        else:
            self.status.alarmOvertemperature.value(0)


        #execute state machine
        self.statemachine[self.activeState]()
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Burner state: " + self.activeState)

        #simulation
        if (self.param.simulation.enable.value() == SIMULATION_ON):
            self.simulationLogic()

        #safety switch off
        if (self.inputs.actTemp.value() > self.param.settings.safetySwitchOffTemperature):
            print("Burner safety switch off triggered: actual temperature: {0}".format(self.inputs.actTemp.value()))
            self.outputs.release.value(0)
        
        #status building
        if (self.inputs.switchedOn.value() == 1):
            self.status.state.value(1)
            self.switchedOnDuration = self.switchedOnDuration + self.samplingTime       #measure time switched on for minimum runtime
        else:
            self.status.state.value(0)
            self.switchedOnDuration = 0

        #log firing duration with a 1-minute resolution
        if (self.oldMinute != datetime.datetime.now().minute):
            self.oldMinute = datetime.datetime.now().minute
            if (self.inputs.switchedOn.value() == 1):
                self.cntMinutesSwitchedOn = self.cntMinutesSwitchedOn + 1 

        #statistics: update PDI variables only every our to avoid too many file writes because these are remanent data
        if (self.oldHour != datetime.datetime.now().hour):
            self.oldHour = datetime.datetime.now().hour
            self.status.dailyOperatingHours.value(self.status.dailyOperatingHours.value() + float(self.cntMinutesSwitchedOn) / 60)
            self.status.annualOperatingHours.value(self.status.annualOperatingHours.value() + float(self.cntMinutesSwitchedOn) / 60)
            self.status.totalOperatingHours.value(self.status.totalOperatingHours.value() + float(self.cntMinutesSwitchedOn) / 60)
            self.cntMinutesSwitchedOn = 0
  
        #reset annual operating hour counter in case of a new year
        if (self.currentYear != datetime.datetime.now().year):
            self.status.annualOperatingHours = 0
            self.currentYear = datetime.datetime.now().year

        #reset daily operating hour counter in case of a new day
        if (self.currentDay != datetime.datetime.now().day):
            self.status.dailyOperatingHours = 0
            self.currentDay = datetime.datetime.now().day
        

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

        #set temperature comes from various sources which result in automatic.setTemperatur finding the maximum value -> limit result to 0 and settings
        self.status.setTemperature.value( max( min(self.param.operatingModes.modes.automatic.setTemperature.value(), self.param.settings.maximumTemperature), 0 ) )

        #two point controller
        if (self.inputs.actTemp.value() < self.status.setTemperature.value() - self.param.settings.hysteresisLow):
            self.outputs.release.value(1)
        if (self.inputs.actTemp.value() > self.status.setTemperature.value() + self.param.settings.hysteresisHigh) and (self.switchedOnDuration > self.param.settings.minOnTime):
            #ensure minimum runtime of burner
            self.outputs.release.value(0)


        
    def sMANUAL(self):
        #leave manual mode in case of new mode
        if (self.param.operatingModes.switch.value() != MANUAL_MODE):
            self.outputs.release.value(0)
            self.activeState = "sIDLE"
            return
        
        #set temperature is given from a manual input value -> limit it to 0 and settings
        self.status.setTemperature.value( max( min(self.param.operatingModes.modes.manual.setTemperature.value(), self.param.settings.maximumTemperature), 0 ) )

        #burner is switched on by manual override
        if (self.param.operatingModes.modes.manual.release.value() == 1):
            if (self.inputs.actTemp.value() < self.status.setTemperature.value() - self.param.settings.hysteresisLow):
                self.outputs.release.value(1)
            if (self.inputs.actTemp.value() > self.status.setTemperature.value() + self.param.settings.hysteresisHigh):
                self.outputs.release.value(0)
        else:
            self.outputs.release.value(0)



    def sSTOP(self):
        #shut down burner
        self.outputs.release.value(0)
        #stay in stop state until all alarms are gone
        if (self.status.alarmOvertemperature.value() == 0) and (self.status.alarmGeneralFailure.value() == 0):
            self.activeState = "sIDLE"
            return


    def simulationLogic(self):
        #no failures during simulation
        self.inputs.generalFailure.value(0)
        self.inputs.overTemperature.value(0)
        
        #override real minimum on time as heat up process takes much less time in simulation
        self.param.settings.minOnTime = self.param.simulation.settings.burnerTemperaturePtTau * 0.1 

        #burner is immediately switched on when release
        self.inputs.switchedOn.value(self.outputs.release.value())

        #simulate temperature behavior
        if (self.inputs.switchedOn.value() == 1):
            self.simTargetTemp = self.param.settings.maximumTemperature
        else:
            self.simTargetTemp = self.param.simulation.settings.environmentalTemperature
        
        #temp = (dt * targetTemp + Tau * temp) ( (dt + Tau)    FIR filter
        self.inputs.actTemp.value( ((self.samplingTime * self.simTargetTemp) + (self.param.simulation.settings.burnerTemperaturePtTau * self.inputs.actTemp.value())) / (self.samplingTime + self.param.simulation.settings.burnerTemperaturePtTau) )
        self.inputs.actTemp.value(max(self.inputs.actTemp.value(), self.param.simulation.settings.environmentalTemperature))

class burnerInputs():
    'Collection of inputs of a certain burner'
    #init
    def __init__(self, PDI):
        self.actTemp = core.modules.iosignal.IOsignal(PDI)
        self.switchedOn = core.modules.iosignal.IOsignal(PDI)
        self.generalFailure = core.modules.iosignal.IOsignal(PDI)
        self.overTemperature = core.modules.iosignal.IOsignal(PDI)

class burnerOutputs():
    'Collection of outputs of a certain burner'
    #init
    def __init__(self, PDI):
        self.release = core.modules.iosignal.IOsignal(PDI)


class burnerParameters:
    #init
    def __init__(self, PDI):
        self.settings = paramSettings()
        self.operatingModes = paramOperatingModes(PDI)
        self.simulation = paramSimulation(PDI)

class paramSettings:
    #init
    def __init__(self):
        self.maximumTemperature = 0.0
        self.safetySwitchOffTemperature = 0.0
        self.minOnTime = 0.0
        self.hysteresisHigh = 0.0
        self.hysteresisLow = 0.0

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
        self.settings = paramSimulationSettings()

class paramSimulationSettings:
    #init
    def __init__(self):
        self.burnerTemperaturePtTau = 0.0
        self.environmentalTemperature = 0.0


class interfaceAutomaticMode:
    #init
    def __init__(self, PDI):
        self.setTemperature = core.modules.iosignal.IOsignal(PDI);

class interfaceManualMode:
    #init
    def __init__(self, PDI):
        self.release = core.modules.iosignal.IOsignal(PDI);
        self.setTemperature = core.modules.iosignal.IOsignal(PDI);


class burnerStatus:
    #init
    def __init__(self, PDI):
        self.state = core.modules.iosignal.IOsignal(PDI);
        self.setTemperature = core.modules.iosignal.IOsignal(PDI);
        self.totalOperatingHours = core.modules.iosignal.IOsignal(PDI);
        self.annualOperatingHours = core.modules.iosignal.IOsignal(PDI);
        self.dailyOperatingHours = core.modules.iosignal.IOsignal(PDI);
        self.alarmOvertemperature = core.modules.iosignal.IOsignal(PDI);
        self.alarmGeneralFailure = core.modules.iosignal.IOsignal(PDI);


#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    
