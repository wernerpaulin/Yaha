#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py

import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import math

import core.modules.iosignal

MODULE_CFG_FILE_NAME = "module.cfg.xml"
MIXER_CFG_ELEMENT_NAME = "./mixers/mixer"
PROCESSTAG_ELEMENT_NAME = "processtag"

AUTOMATIC_MODE = 0
MANUAL_MODE = 1

MIXER_STATE_STOPPED = 0
MIXER_STATE_CLOSING = 1
MIXER_STATE_OPENING = 2
MIXER_STATE_HOMING_INVALID = 3


def init(PDI):
    global Mixers
    Mixers = dict()
    attrList = [] 
    mixerID = None

    #read module configuration and initialize each mixer
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for mixerCfg in cfgRoot.findall(MIXER_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                mixerID = mixerCfg.get('id')
                Mixers[mixerID] = mixerManager(PDI)

                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Mixers[mixerID].inputs)      #['alarmPumpSafetyReleaseOff',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="switchedOn">
                    inputCfg = mixerCfg.find('.//inputs/input[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Mixers[mixerID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)
                
                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(Mixers[mixerID].outputs)      #['open',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = mixerCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Mixers[mixerID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)


                #initialize settings parameter
                settingsNameList = getClassAttributes(Mixers[mixerID].param.settings)      #['fullyOpenTime', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = mixerCfg.find('.//parameters/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Mixers[mixerID].param.settings, settingName, float(settingCfg.text))
                
                #initialize operating modes parameter
                #switch
                operatingSwitchCfg = mixerCfg.find('.//parameters/operatingmodes/switch')
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
                        ioSignalInst = getattr(Mixers[mixerID].param.operatingModes, "switch")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                
                
                #modes
                operatingModeNameList = getClassAttributes(Mixers[mixerID].param.operatingModes.modes)      #['automatic', ...]
                #try to find the corresponding entry in the configuration file 
                for operatingModeName in operatingModeNameList:
                    operatingModeCfg = mixerCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]')
                    #continue only if configuration exists
                    if operatingModeCfg != None:
                        #access operating mode infrastructure and initialize interfaces
                        operatingModeObj = getattr(Mixers[mixerID].param.operatingModes.modes, operatingModeName)
                        interfaceNameList = getClassAttributes(operatingModeObj)      #['setPosition', ...]
                        #try to find settings for all found interfaces
                        for interfaceName in interfaceNameList:
                            interfaceCfg = mixerCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]' + '/interfaces/interface[@name="' + interfaceName + '"]')
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

                #initialize status points
                ioNameList = getClassAttributes(Mixers[mixerID].status)      #['state', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    statusCfg = mixerCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Mixers[mixerID].status, ioName)              #get access to IO signal: "state", "setTemperature",...
                            ioSignalInst.addProcessTag(processTag.text, None)

            except Exception as e:
                print("Loading configuration for mixer <{0}> failed: {1}".format(mixerID, e))
                return    

    except Exception as e:
        print("Loading mixers module configuration <{0}> failed: {1}".format(mixerID, e))
        return    





class mixerManager:
    "Control of mixers"
    #init
    def __init__(self, PDI):
        self.inputs = mixerInputs(PDI)
        self.outputs = mixerOutputs(PDI)
        self.param = mixerParameters(PDI)
        self.status = mixerStatus(PDI)

        
        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sAUTOMATIC": self.sAUTOMATIC,
                             "sMANUAL": self.sMANUAL,
                             "sHOMING": self.sHOMING,
                             "sMOVE_OPEN": self.sMOVE_OPEN,
                             "sMOVE_CLOSE": self.sMOVE_CLOSE,
                             "sMOVE_STOP": self.sMOVE_STOP,
                             "sALARM_CLOSE_MIXER": self.sALARM_CLOSE_MIXER
                            }
        
        self.activeState = "sIDLE"
        self.activeStateOld = ""
        self.oldMinute = datetime.datetime.now().minute
                
        self.homingValid = False
        self.startTimeMovement = 0
        self.startTimeHoming = 0
        self.lastStopPosition = 0
        self.newActPosition = 0
        self.operatingModeBeforeMovement = 0



    #cyclic logic    
    def update(self, PDI):
        #check time every minute
        if (self.oldMinute != datetime.datetime.now().minute):
            self.oldMinute = datetime.datetime.now().minute
            #initate homing every day at midnight
            if (datetime.datetime.now().hour == 0) and (datetime.datetime.now().minute == 0):
                self.homingValid = False
                
        #execute state machine
        self.statemachine[self.activeState]()
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Mixer state: " + self.activeState)

        #mixer state and actual position generation
        deltaPosPerSec = (self.param.settings.fullyOpenPosition - self.param.settings.fullyClosedPosition) / self.param.settings.fullyOpenTime
        

        #not yet homed
        if (self.homingValid != True):
            self.status.state.value(MIXER_STATE_HOMING_INVALID)
        #opening
        elif (self.outputs.open.value() == 1):
            self.status.state.value(MIXER_STATE_OPENING)
            self.newActPosition = self.lastStopPosition + ((time.time() - self.startTimeMovement) * deltaPosPerSec)
        #closing    
        elif (self.outputs.close.value() == 1):
            self.status.state.value(MIXER_STATE_CLOSING)
            self.newActPosition = self.lastStopPosition - ((time.time() - self.startTimeMovement) * deltaPosPerSec)
        #mixer stopped    
        else:
            self.status.state.value(MIXER_STATE_STOPPED)
            self.startTimeMovement = time.time()
            self.lastStopPosition = self.status.actPosition.value()
            self.operatingModeBeforeMovement = self.param.operatingModes.switch.value()
        
        #limit calculated position
        self.newActPosition = max(min(self.newActPosition, self.param.settings.fullyOpenPosition), self.param.settings.fullyClosedPosition)
        self.status.actPosition.value(self.newActPosition)
        
    def sIDLE(self):
        #alarm handling (optional)
        try:
            if (self.inputs.alarmPumpSafetyReleaseOff.value() == 1):
                self.outputs.close.value(0)
                self.outputs.open.value(0)
                self.activeState = "sALARM_CLOSE_MIXER"
                return
        except:
            pass
        
        #first do homing
        if (self.homingValid != True):
            self.activeState = "sHOMING"
            self.startTimeHoming = time.time()
            return

        if (self.param.operatingModes.switch.value() == AUTOMATIC_MODE):
            self.activeState = "sAUTOMATIC"
        elif (self.param.operatingModes.switch.value() == MANUAL_MODE):
            self.activeState = "sMANUAL"
        
    def sAUTOMATIC(self):
        #alarm handling (optional)
        try:
            if (self.inputs.alarmPumpSafetyReleaseOff.value() == 1):
                self.outputs.close.value(0)
                self.outputs.open.value(0)
                self.activeState = "sALARM_CLOSE_MIXER"
                return
        except:
            pass

        #leave automatic mode in case of new mode
        if (self.param.operatingModes.switch.value() != AUTOMATIC_MODE) or (self.homingValid != True):
            self.activeState = "sIDLE"
            return

        #start moving mixer only in case of new set position is out of zero window to avoid constant short movement
        if (abs(self.param.operatingModes.modes.automatic.setPosition.value() - self.status.actPosition.value()) >= self.param.settings.zeroWindow):
            #set new target position
            self.status.setPosition.value(self.param.operatingModes.modes.automatic.setPosition.value())
            if (self.status.setPosition.value() >= self.status.actPosition.value()):
                self.activeState = "sMOVE_OPEN"
                return
            else:
                self.activeState = "sMOVE_CLOSE"
                return

        
    def sMANUAL(self):
        #alarm handling (optional)
        try:
            if (self.inputs.alarmPumpSafetyReleaseOff.value() == 1):
                self.outputs.close.value(0)
                self.outputs.open.value(0)
                self.activeState = "sALARM_CLOSE_MIXER"
                return
        except:
            pass

        #invalid homing flag if manually requested
        if (self.param.operatingModes.modes.manual.cmdHoming.value() == 1):
            self.homingValid = False
            self.activeState = "sMOVE_STOP"
            return
        
        #leave manual mode in case of new mode
        if (self.param.operatingModes.switch.value() != MANUAL_MODE) or (self.homingValid != True):
            self.activeState = "sMOVE_STOP"
            return
        
        #start moving mixer only in case of new set position is out of zero window to avoid constant short movement
        if (abs(self.param.operatingModes.modes.manual.setPosition.value() - self.status.actPosition.value()) >= self.param.settings.zeroWindow):
            #set new target position
            self.status.setPosition.value(self.param.operatingModes.modes.manual.setPosition.value())
            if (self.status.setPosition.value() >= self.status.actPosition.value()):
                self.activeState = "sMOVE_OPEN"
                return
            else:
                self.activeState = "sMOVE_CLOSE"
                return

    def sHOMING(self):
        #close mixer 50% longer than time to fully open mixer
        if (time.time() - self.startTimeHoming) > (self.param.settings.fullyOpenTime * 1.5):
            self.homingValid = True     #set homing flag
            self.activeState = "sMOVE_STOP"
            return
        else:
            self.outputs.close.value(1)       #close mixer fully
            self.outputs.open.value(0)
            
    def sMOVE_OPEN(self):
        #alarm handling (optional)
        try:
            if (self.inputs.alarmPumpSafetyReleaseOff.value() == 1):
                self.outputs.close.value(0)
                self.outputs.open.value(0)
                self.activeState = "sALARM_CLOSE_MIXER"
                return
        except:
            pass

        #opening
        self.outputs.close.value(0)
        self.outputs.open.value(1)
        #wait until in position or when operating mode changed automatic/manual
        if (self.status.actPosition.value() >= self.status.setPosition.value()) or (self.operatingModeBeforeMovement != self.param.operatingModes.switch.value()):
            self.activeState = "sMOVE_STOP"
            return
    
    def sMOVE_CLOSE(self):
        #alarm handling (optional)
        try:
            if (self.inputs.alarmPumpSafetyReleaseOff.value() == 1):
                self.outputs.close.value(0)
                self.outputs.open.value(0)
                self.activeState = "sALARM_CLOSE_MIXER"
                return
        except:
            pass

        #closing
        self.outputs.close.value(1)
        self.outputs.open.value(0)
        #wait until in position or when operating mode changed automatic/manual
        if (self.status.actPosition.value() <= self.status.setPosition.value()) or (self.operatingModeBeforeMovement != self.param.operatingModes.switch.value()):
            self.activeState = "sMOVE_STOP"
            return

    def sMOVE_STOP(self):
        #stopping
        self.outputs.close.value(0)
        self.outputs.open.value(0)
        self.activeState = "sIDLE"
        return
        
    def sALARM_CLOSE_MIXER(self):
        #in case of an alarm, close mixer to ensure only colder water flows into pipes 
        if (self.status.actPosition.value() <= self.param.settings.fullyClosedPosition):
            self.outputs.close.value(0)
            self.outputs.open.value(0)
        else:
            self.outputs.close.value(1)
            self.outputs.open.value(0)
        
        #stay in alarm state until alarm is gone
        if (self.inputs.alarmPumpSafetyReleaseOff.value() == 0):
            self.outputs.close.value(0)
            self.outputs.open.value(0)
            self.activeState = "sIDLE"
            return            

def update(PDI):
    global Mixers
    '''
    Functional description    
    automatic/manual mode
    automatic homing every day at midnight
    in case of safety release off of pump mixer closes completely to get cooler water into the circuit
    '''
    for mixer in Mixers:
        Mixers[mixer].update(PDI)


class mixerInputs():
    'Collection of inputs of a certain mixer'
    #init
    def __init__(self, PDI):
        self.alarmPumpSafetyReleaseOff = core.modules.iosignal.IOsignal(PDI)

class mixerOutputs():
    'Collection of outputs of a certain mixer'
    #init
    def __init__(self, PDI):
        self.open = core.modules.iosignal.IOsignal(PDI)
        self.close = core.modules.iosignal.IOsignal(PDI)


class mixerParameters:
    #init
    def __init__(self, PDI):
        self.settings = paramSettings()
        self.operatingModes = paramOperatingModes(PDI)

class paramSettings:
    #init
    def __init__(self):
        self.fullyOpenTime = 0.0
        self.fullyOpenPosition = 0.0
        self.fullyClosedPosition = 0.0
        self.zeroWindow = 0.0

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

class interfaceAutomaticMode:
    #init
    def __init__(self, PDI):
        self.setPosition = core.modules.iosignal.IOsignal(PDI);

class interfaceManualMode:
    #init
    def __init__(self, PDI):
        self.setPosition = core.modules.iosignal.IOsignal(PDI);
        self.cmdHoming = core.modules.iosignal.IOsignal(PDI);


class mixerStatus:
    #init
    def __init__(self, PDI):
        self.state = core.modules.iosignal.IOsignal(PDI);
        self.actPosition = core.modules.iosignal.IOsignal(PDI);
        self.setPosition = core.modules.iosignal.IOsignal(PDI);

#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    
