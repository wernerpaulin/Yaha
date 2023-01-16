#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import math

import core.modules.iosignal

MODULE_CFG_FILE_NAME = "module.cfg.xml"
ROOM_CFG_ELEMENT_NAME = "./rooms/room"
PROCESSTAG_ELEMENT_NAME = "processtag"

AUTOMATIC_MODE = 0
MANUAL_MODE = 1
SIMULATION_ON = 1

SATURDAY_INDEX = 5
SUNDAY_INDEX = 6

GLOBAL_MODE_OFF = 0
GLOBAL_MODE_ON = 1
GLOBAL_MODE_SUSPEND = 2
GLOBAL_MODE_NOT_AT_HOME = 3

ROOM_MODE_AUTOMATIC = 0
ROOM_MODE_ALWAYS_COMFORT = 1
ROOM_MODE_ALWAYS_REDUCED = 2

HEATING_STATE_COMFORT = 1
HEATING_STATE_REDUCED = 0

HEATING_CONTROLLER_ON = 1
HEATING_CONTROLLER_OFF = 0

MIXER_STATE_HOMING_INVALID = 3

PUMP_STATE_ON = 1


def init(PDI):
    global Rooms
    Rooms = dict()
    attrList = [] 
    roomID = None

    #read module configuration and initialize each room
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for roomCfg in cfgRoot.findall(ROOM_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                roomID = roomCfg.get('id')
                Rooms[roomID] = roomManager(PDI)
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Rooms[roomID].inputs)      #['burnerActTemp', 'burnerSetTemp',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="switchedOn">
                    inputCfg = roomCfg.find('.//inputs/input[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Rooms[roomID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(Rooms[roomID].outputs)      #['pumpRelease',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = roomCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Rooms[roomID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)


                #initialize settings parameter
                settingsNameList = getClassAttributes(Rooms[roomID].param.settings)      #['hysteresisHigh', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = roomCfg.find('.//parameters/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Rooms[roomID].param.settings, settingName, float(settingCfg.text))
                
                #initialize operating modes parameter
                #switch
                operatingSwitchCfg = roomCfg.find('.//parameters/operatingmodes/switch')
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
                        ioSignalInst = getattr(Rooms[roomID].param.operatingModes, "switch")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                
                
                #modes
                operatingModeNameList = getClassAttributes(Rooms[roomID].param.operatingModes.modes)      #['automatic', ...]
                #try to find the corresponding entry in the configuration file 
                for operatingModeName in operatingModeNameList:
                    operatingModeCfg = roomCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]')
                    #continue only if configuration exists
                    if operatingModeCfg != None:
                        #access operating mode infrastructure and initialize interfaces
                        operatingModeObj = getattr(Rooms[roomID].param.operatingModes.modes, operatingModeName)
                        interfaceNameList = getClassAttributes(operatingModeObj)      #['setTemperature', ...]
                        #try to find settings for all found interfaces
                        for interfaceName in interfaceNameList:
                            interfaceCfg = roomCfg.find('.//parameters/operatingmodes/operatingmode[@name="' + operatingModeName + '"]' + '/interfaces/interface[@name="' + interfaceName + '"]')
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
                simulationEnableCfg = roomCfg.find('.//parameters/simulation/enable')
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
                        ioSignalInst = getattr(Rooms[roomID].param.simulation, "enable")              #get access to IO signal: "up", "down",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                                

                #settings
                settingsNameList = getClassAttributes(Rooms[roomID].param.simulation.settings)      #['burnerTemperaturePtTau', ...]
                #try to find the corresponding entry in the configuration file 
                for settingName in settingsNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    settingCfg = roomCfg.find('.//parameters/simulation/settings/setting[@name="' + settingName + '"]')
                    #continue only if configuration exists
                    if settingCfg != None:                
                        setattr(Rooms[roomID].param.simulation.settings, settingName, float(settingCfg.text))


                #initialize status points
                ioNameList = getClassAttributes(Rooms[roomID].status)      #['state', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    statusCfg = roomCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Rooms[roomID].status, ioName)              #get access to IO signal: "state", "setTemperature",...
                            ioSignalInst.addProcessTag(processTag.text, None)

            except Exception as e:
                print("Loading configuration for room <{0}> failed: {1}".format(roomID, e))
                return    

    except Exception as e:
        print("Loading rooms module configuration <{0}> failed: {1}".format(roomID, e))
        return    






def update(PDI):
    global Rooms
    '''
    Functional description    

    '''
    for room in Rooms:
        Rooms[room].update(PDI)



class roomManager:
    "Control of Rooms"
    #init
    def __init__(self, PDI):
        self.inputs = roomInputs(PDI)
        self.outputs = roomOutputs(PDI)
        self.param = roomParameters(PDI)
        self.status = roomStatus(PDI)

        self.suspendStartTime = time.time()
        self.modeBeforeSuspend = GLOBAL_MODE_OFF
        
        self.currentWeekdayIndex = 0
        
        self.notAtHomeActive = False
        
        self.simRoomTemperatureP1 = core.modules.filter.PT1()
        self.simFlowTemperatureP1 = core.modules.filter.PT1()
        self.simTargetRoomTemp = 0
        self.simTargetFlowTemp = 0
        
        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sAUTOMATIC": self.sAUTOMATIC,
                             "sMANUAL": self.sMANUAL,
                             "sWAIT_MIXER_READY": self.sWAIT_MIXER_READY
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""


    #cyclic logic    
    def update(self, PDI):
        #execute state machine
        self.statemachine[self.activeState]()
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Room state: " + self.activeState)

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

        #abort automatic mode as long as mixer is not ready
        if (self.inputs.mixerState.value() == MIXER_STATE_HOMING_INVALID):
            self.activeState = "sWAIT_MIXER_READY"
            return
        
        #find set temperature for room depending on heating modes
        #GLOBAL_MODE_ON or GLOBAL_MODE_NOT_AT_HOME
        if (self.param.operatingModes.modes.automatic.globalMode.value() == GLOBAL_MODE_ON) or (self.param.operatingModes.modes.automatic.globalMode.value() == GLOBAL_MODE_NOT_AT_HOME):
            #evaluate not at home status
            try:
                #merge date and time string and convert to datetime object
                leavingDateString = self.param.operatingModes.modes.automatic.notAtHomeStartDate.value() + " " + self.param.operatingModes.modes.automatic.notAtHomeStartTime.value()
                leavingDate = datetime.datetime.strptime(leavingDateString, '%Y-%m-%d %H:%M')

                backHomeDateString = self.param.operatingModes.modes.automatic.notAtHomeEndDate.value() + " " + self.param.operatingModes.modes.automatic.notAtHomeEndTime.value()
                backHomeDate = datetime.datetime.strptime(backHomeDateString, '%Y-%m-%d %H:%M')
                
                if (leavingDate <= datetime.datetime.today() < backHomeDate):
                    self.notAtHomeActive = True
                else:
                    self.notAtHomeActive = False
                
            except Exception as e:
                print("Not at home calculation error: <{0}>".format(e))
                self.notAtHomeActive = False     
            
            #in case current date and time falls into not at home period -> overrule room mode and set room temperature to reduced
            if (self.notAtHomeActive == True):
                self.status.setRoomTemperature.value(self.param.operatingModes.modes.automatic.roomReducedSetTemp.value())

            #ROOM_MODE_AUTOMATIC
            elif (self.param.operatingModes.modes.automatic.roomMode.value() == ROOM_MODE_AUTOMATIC):
                #in automatic mode comfort or reduced temperature depends on time and day of week
                #WEEKEND
                if (self.currentWeekdayIndex == SATURDAY_INDEX) or (self.currentWeekdayIndex == SUNDAY_INDEX):
                    try:
                        #convert start and end time string into a time object
                        startTime = time.strptime(self.param.operatingModes.modes.automatic.weekendStartTime.value(), '%H:%M')
                        endTime = time.strptime(self.param.operatingModes.modes.automatic.weekendEndTime.value(), '%H:%M')
                        
                        #remove date information of current time because comparison would fail as start and end time have no date
                        currentTimeString = str(datetime.datetime.today().hour) + ":" + str(datetime.datetime.today().minute)
                        currentTime = time.strptime(currentTimeString, '%H:%M')
                        
                        #check whether current time is within heating phase
                        if (startTime <= currentTime <= endTime):
                            #within heating phase set temperature is comfort temperature
                            self.status.setRoomTemperature.value(self.param.operatingModes.modes.automatic.roomComfortSetTemp.value())
                        else:
                            #outside heating phase set temperature is reduced temperature
                            self.status.setRoomTemperature.value(self.param.operatingModes.modes.automatic.roomReducedSetTemp.value())

                    except Exception as e:
                        print("Room weekend phase configuration error: {0}".format(e))
                        self.status.setRoomTemperature.value(0)
                #WEEKDAYS
                else:
                    try:
                        #convert start and end time string into a time object
                        startTime = time.strptime(self.param.operatingModes.modes.automatic.weekdayStartTime.value(), '%H:%M')
                        endTime = time.strptime(self.param.operatingModes.modes.automatic.weekdayEndTime.value(), '%H:%M')
                        
                        #remove date information of current time because comparison would fail as start and end time have no date
                        currentTimeString = str(datetime.datetime.today().hour) + ":" + str(datetime.datetime.today().minute)
                        currentTime = time.strptime(currentTimeString, '%H:%M')
                        
                        #check whether current time is within heating phase
                        if (startTime <= currentTime <= endTime):
                            #within heating phase set temperature is comfort temperature
                            self.status.setRoomTemperature.value(self.param.operatingModes.modes.automatic.roomComfortSetTemp.value())
                        else:
                            #outside heating phase set temperature is reduced temperature
                            self.status.setRoomTemperature.value(self.param.operatingModes.modes.automatic.roomReducedSetTemp.value())

                    except Exception as e:
                        print("Room weekday phase configuration error: {0}".format(e))
                        self.status.setRoomTemperature.value(0)
            
            #ROOM_MODE_ALWAYS_COMFORT   
            elif (self.param.operatingModes.modes.automatic.roomMode.value() == ROOM_MODE_ALWAYS_COMFORT):
                #always on - comfort temperature
                self.status.setRoomTemperature.value(self.param.operatingModes.modes.automatic.roomComfortSetTemp.value())
            
            #ROOM_MODE_ALWAYS_REDUCED
            elif (self.param.operatingModes.modes.automatic.roomMode.value() == ROOM_MODE_ALWAYS_REDUCED):
                #always on - reduced temperature
                self.status.setRoomTemperature.value(self.param.operatingModes.modes.automatic.roomReducedSetTemp.value())
            
            #UNKNOWN
            else:
                print("ROOM: unknown room mode <{0}>".format(self.param.operatingModes.modes.automatic.roomMode.value()))
                self.param.operatingModes.modes.automatic.roomMode.value(ROOM_MODE_AUTOMATIC)

        #GLOBAL_MODE_SUSPEND
        elif (self.param.operatingModes.modes.automatic.globalMode.value() == GLOBAL_MODE_SUSPEND):
            #suspend only for a limited time
            if ((time.time() - self.suspendStartTime) > self.param.settings.offDurationForVentilation):
                #switch back to the mode before suspend
                self.param.operatingModes.modes.automatic.globalMode.value(self.modeBeforeSuspend)
            else:
                #during suspend
                self.status.setRoomTemperature.value(0) #heating fully stopped

        #GLOBAL_MODE_OFF
        elif (self.param.operatingModes.modes.automatic.globalMode.value() == GLOBAL_MODE_OFF):
            self.status.setRoomTemperature.value(0)
        
        #UNKNOWN
        else:
            print("ROOM: unknown global mode <{0}>".format(self.param.operatingModes.modes.automatic.globalMode.value()))
            self.param.operatingModes.modes.automatic.globalMode.value(GLOBAL_MODE_OFF)
        
        #generate heating state
        if (self.status.setRoomTemperature.value() == self.param.operatingModes.modes.automatic.roomComfortSetTemp.value()):
            self.status.heatingState.value(HEATING_STATE_COMFORT)
        else:
            self.status.heatingState.value(HEATING_STATE_REDUCED)
        
        #remember start time when mode is switched to suspend mode
        if (self.param.operatingModes.modes.automatic.globalMode.value() != GLOBAL_MODE_SUSPEND):
            self.suspendStartTime = time.time()
            self.modeBeforeSuspend = self.param.operatingModes.modes.automatic.globalMode.value()


        #2-point controller for room -> gives a set temperature for flow based on room temperature and outside temperature
        self.roomController()

        #PDI control of mixer -> gives a set position for the mixer
        self.flowController()


        #Pump and burner handling: if there is a valid set temperature, the PID works
        if (self.status.setFlowTemperature.value() != 0):
            self.outputs.burnerSetTemp.value(self.status.setFlowTemperature.value() + self.param.settings.burnerSetTempOffset)
            self.outputs.pumpRelease.value(1)
        else:
            #set set temperature for flow: switch off pump and burner
            self.outputs.burnerSetTemp.value(0)
            self.outputs.pumpRelease.value(0)

    def sMANUAL(self):
        #leave manual mode in case of new mode
        if (self.param.operatingModes.switch.value() != MANUAL_MODE):
            self.activeState = "sIDLE"
            return
        
        #in manual mode pump and/or mixer are operated manually: set temperature = 0°C
        self.status.setFlowTemperature.value(0)

    def sWAIT_MIXER_READY(self):
        #do not start PID as long as mixer is not ready
        if (self.inputs.mixerState.value() != MIXER_STATE_HOMING_INVALID):
            self.activeState = "sIDLE"
            return

    def simulationLogic(self):
        #define outside temperature
        self.inputs.actTempOutside.value(self.param.simulation.settings.outsideTemperature)
        
        
        #simulate flow temperature behavior for room and limit drop to environment temperature
        if (self.inputs.pumpState.value() == PUMP_STATE_ON):
            self.simTargetFlowTemp = (self.inputs.actTempBurner.value() * (self.inputs.mixerActPosition.value() / 100)) + (self.inputs.actTempBurner.value() * self.param.settings.returnFlowTempDrop * ((100 - self.inputs.mixerActPosition.value()) / 100))
        else:
            self.simTargetFlowTemp = self.param.simulation.settings.environmentalTemperature

        
        #PT1 path of flow temperature
        self.inputs.actTempFlow.value(self.simFlowTemperatureP1.update(self.simTargetFlowTemp, self.param.simulation.settings.flowTemperaturePtTau, 1))
        self.inputs.actTempFlow.value( max(self.inputs.actTempFlow.value(), self.param.simulation.settings.environmentalTemperature) )
        
        
        #simulate room temperature behavior for room and limit drop to environment temperature
        if (self.inputs.pumpState.value() == PUMP_STATE_ON):
            self.simTargetRoomTemp = self.inputs.actTempFlow.value() * self.param.simulation.settings.flowToRoomConversionRate   #depending on actual flow temperature the room temperature will reach a certain value
        else:
            self.simTargetRoomTemp = self.param.simulation.settings.environmentalTemperature

        #PT1 path of room temperature
        self.inputs.actTempRoom.value(self.simRoomTemperatureP1.update(self.simTargetRoomTemp, self.param.simulation.settings.roomTemperaturePtTau, 1))
        self.inputs.actTempRoom.value( max(self.inputs.actTempRoom.value(), self.param.simulation.settings.environmentalTemperature) )

    def roomController(self):
        #2-point controller for room
        if (self.inputs.actTempRoom.value() < self.status.setRoomTemperature.value() - self.param.settings.hysteresisLow):
            #calculate set temperature of flow from outside temperature and room set temperature
            self.status.setFlowTemperature.value( self.calcFlowSetTemp(self.status.setRoomTemperature.value(), 
                                                                       self.param.operatingModes.modes.automatic.heatCurveSlope.value(),
                                                                       self.param.operatingModes.modes.automatic.heatCurveLevel.value(),
                                                                       self.inputs.actTempOutside.value(),
                                                                       self.param.settings.maxFlowTemp) )

        if (self.inputs.actTempRoom.value() > self.status.setRoomTemperature.value() + self.param.settings.hysteresisHigh):
            self.status.setFlowTemperature.value(0)


    def calcFlowSetTemp(self, t_room_set, slope, level, t_outside, t_flow_max):
        #heat curve formula (Viessmann)
        t_flow = t_room_set + slope * 20 * math.pow(((t_room_set-t_outside)/20), 0.8) + level
        return (min(t_flow, t_flow_max))
        
    
    def flowController(self):
        #PID controller for flow temperature
        "TODO: Regler einbauen"
        if (self.status.setFlowTemperature.value() != 0):
            self.status.controllerState.value(HEATING_CONTROLLER_ON)
            "TEST CODE"
            self.outputs.mixerSetPosition.value(50.0)
            
            "TODO: Vorlauftemperatur über Mischer begrenzen wenn Brenner zu heiss ist 20% über Vorlaufsoll (möglichst generisch lösen)"
        else:
            self.status.controllerState.value(HEATING_CONTROLLER_OFF)
            #close mixer if no flow temperarue is required (PID is off)
            self.outputs.mixerSetPosition.value(0)



class roomInputs():
    'Collection of inputs of a certain room'
    #init
    def __init__(self, PDI):
        self.actTempFlow = core.modules.iosignal.IOsignal(PDI)
        self.actTempOutside = core.modules.iosignal.IOsignal(PDI)
        self.actTempBurner = core.modules.iosignal.IOsignal(PDI)
        self.actTempRoom = core.modules.iosignal.IOsignal(PDI)
        self.mixerState = core.modules.iosignal.IOsignal(PDI)
        self.mixerActPosition = core.modules.iosignal.IOsignal(PDI)
        self.pumpState = core.modules.iosignal.IOsignal(PDI)

class roomOutputs():
    'Collection of outputs of a certain room'
    #init
    def __init__(self, PDI):
        self.burnerSetTemp = core.modules.iosignal.IOsignal(PDI)
        self.pumpRelease = core.modules.iosignal.IOsignal(PDI)
        self.mixerSetPosition = core.modules.iosignal.IOsignal(PDI)

class roomParameters:
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
        self.pidKp = 0.0
        self.pidTn = 0.0
        self.Ymax = 0.0
        self.Ymin = 0.0
        self.burnerSetTempOffset = 0.0
        self.offDurationForVentilation = 0.0
        self.maxFlowTemp = 0.0
        self.returnFlowTempDrop = 0.0

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
        self.roomTemperaturePtTau = 0.0
        self.flowTemperaturePtTau = 0.0
        self.environmentalTemperature = 0.0
        self.outsideTemperature = 0.0
        self.flowToRoomConversionRate = 0.0


class interfaceAutomaticMode:
    #init
    def __init__(self, PDI):
        self.globalMode = core.modules.iosignal.IOsignal(PDI);
        self.notAtHomeStartDate = core.modules.iosignal.IOsignal(PDI);
        self.notAtHomeStartTime = core.modules.iosignal.IOsignal(PDI);
        self.notAtHomeEndDate = core.modules.iosignal.IOsignal(PDI);
        self.notAtHomeEndTime = core.modules.iosignal.IOsignal(PDI);
        self.roomMode = core.modules.iosignal.IOsignal(PDI);
        self.roomComfortSetTemp = core.modules.iosignal.IOsignal(PDI);
        self.roomReducedSetTemp = core.modules.iosignal.IOsignal(PDI);
        self.weekdayStartTime = core.modules.iosignal.IOsignal(PDI);
        self.weekdayEndTime = core.modules.iosignal.IOsignal(PDI);
        self.weekendStartTime = core.modules.iosignal.IOsignal(PDI);
        self.weekendEndTime = core.modules.iosignal.IOsignal(PDI);
        self.heatCurveLevel = core.modules.iosignal.IOsignal(PDI);
        self.heatCurveSlope = core.modules.iosignal.IOsignal(PDI);


class roomStatus:
    #init
    def __init__(self, PDI):
        self.heatingState = core.modules.iosignal.IOsignal(PDI);
        self.controllerState = core.modules.iosignal.IOsignal(PDI);
        self.setRoomTemperature = core.modules.iosignal.IOsignal(PDI);
        self.setFlowTemperature = core.modules.iosignal.IOsignal(PDI);


#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    