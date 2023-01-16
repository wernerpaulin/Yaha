#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py


MODULE_CFG_FILE_NAME = "module.cfg.xml"
BLIND_CFG_ELEMENT_NAME = "./blinds/blind"
GROUP_CFG_ELEMENT_NAME = "./groupcontrol/groups/group"

PROCESSTAG_ELEMENT_NAME = "processtag"
OUTPUTMODE_ELEMENT_NAME = "outputmode"
ENABLE_ELEMENT_NAME = "enable"
EVENT_ELEMENT_NAME = "event"
DATERANGES_ELEMENT_NAME = "dateranges"
DATERANGE_ELEMENT_NAME = "daterange"
START_ELEMENT_NAME = "start"
END_ELEMENT_NAME = "end"
WEEKDAYS_ELEMENT_NAME = "weekdays"
WEEKDAY_ELEMENT_NAME = "weekday"
EVENT_ACTION_OPEN = "open"
EVENT_ACTION_CLOSE = "close"
EVENT_ACTION_OPEN_AT_SUNRISE = "openAtSunrise"
EVENT_ACTION_CLOSE_AT_SUNSET = "closeAtSunset"
START_DELAY_ELEMENT_NAME = "start"
STOP_DELAY_ELEMENT_NAME = "stop"
MOTOR_POSITION_FULLY_OPEN_ELEMENT_NAME = "motorposfullyopen"
MOTOR_POSITION_FULLY_CLOSED_ELEMENT_NAME = "motorposfullyclosed"
MOTOR_STOP_DELAY_DURATION_ELEMENT_NAME = "motorstopdelay"
POSITION_ELEMENT_NAME = "position"
SIZE_ELEMENT_NAME = "size"
OBSERVER_ELEMENT_NAME = "observer"
AZIMUTH_ELEMENT_NAME = "azimuth"

FULLY_OPEN_POS = 0
FULLY_CLOSED_POS = 100
VALID_POS_TIMEOUT = 20 #s timeout between two samples if closing or opening indicate movement but stop is not flagged

import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import math

import core.modules.iosignal
from core.modules.cal_event import *

from core.modules.astral import Astral


def init(PDI):
    global Blinds
    Blinds = dict()
    attrList = []    

    global ControlGroups
    ControlGroups = dict()


    #read module configuration and initialize each device
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of blinds
        for blindCfg in cfgRoot.findall(BLIND_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                blindID = blindCfg.get('id')
                Blinds[blindID] = blindManager(PDI)
                Blinds[blindID].blindID = blindID
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Blinds[blindID].inputs)      #['open', 'close',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="on">
                    inputCfg = blindCfg.find('.//inputs/input[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Blinds[blindID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(Blinds[blindID].outputs)      #['open', 'close', 'teach']
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = blindCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(Blinds[blindID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)
                    
                #initialize window parameter
                windowCfg = blindCfg.find('.//parameters/window')
                #continue only if configuration exists
                if windowCfg != None:
                    #get window parameters
                    cfgItem = windowCfg.find(POSITION_ELEMENT_NAME)
                    Blinds[blindID].param.window.orientation = float(cfgItem.attrib['orientation'])

                    cfgItem = windowCfg.find(SIZE_ELEMENT_NAME)
                    Blinds[blindID].param.window.height = float(cfgItem.attrib['height'])
                    Blinds[blindID].param.window.floorDistance = float(cfgItem.attrib['floordistance'])

                    cfgItem = windowCfg.find(MOTOR_POSITION_FULLY_OPEN_ELEMENT_NAME)
                    Blinds[blindID].param.window.motorPosFullyOpen = float(cfgItem.attrib['position'])

                    cfgItem = windowCfg.find(MOTOR_POSITION_FULLY_CLOSED_ELEMENT_NAME)
                    Blinds[blindID].param.window.motorPosFullyClosed = float(cfgItem.attrib['position'])

                    cfgItem = windowCfg.find(MOTOR_STOP_DELAY_DURATION_ELEMENT_NAME)
                    Blinds[blindID].param.window.motorStopDelay = float(cfgItem.attrib['duration'])

                    #initialize blind/motor movement linearization (all parameters are normalized to 0..100)
                    #x-axis: motor position
                    Blinds[blindID].blindPosLin.x1 = Blinds[blindID].param.window.motorPosFullyOpen
                    Blinds[blindID].blindPosLin.x2 = Blinds[blindID].param.window.motorPosFullyClosed
                    #y-axis: blind position
                    Blinds[blindID].blindPosLin.y1 = FULLY_OPEN_POS
                    Blinds[blindID].blindPosLin.y2 = FULLY_CLOSED_POS

                    Blinds[blindID].blindPosLin.xMin = FULLY_OPEN_POS
                    Blinds[blindID].blindPosLin.xMax = FULLY_CLOSED_POS
                    Blinds[blindID].blindPosLin.yMin = FULLY_OPEN_POS
                    Blinds[blindID].blindPosLin.yMax = FULLY_CLOSED_POS

                    Blinds[blindID].blindPosLin.calcK()
                    Blinds[blindID].blindPosLin.calcD()
                    
                    
                    

                #initialize auto shading
                autoShadingCfg = blindCfg.find('.//parameters/autoshading')
                #continue only if configuration exists
                if autoShadingCfg != None:
                    #link enable signal with PDI
                    enableCfg = autoShadingCfg.find(ENABLE_ELEMENT_NAME)
                    #get mapped PDI process tag: <processtag>xxx</processtag>
                    processTag = enableCfg.find(PROCESSTAG_ELEMENT_NAME)                 
                    #each IOsignal has an addProcessTag function: call it generically depending on ioName
                    ioSignalInst = getattr(Blinds[blindID].param.autoShading, ENABLE_ELEMENT_NAME)
                    ioSignalInst.addProcessTag(processTag.text, None)                    

                    #get auto shading parameters
                    cfgItem = autoShadingCfg.find(OBSERVER_ELEMENT_NAME)
                    Blinds[blindID].param.autoShading.observer.height = float(cfgItem.attrib['height'])
                    Blinds[blindID].param.autoShading.observer.windowDistance = float(cfgItem.attrib['windowdistance'])

                    cfgItem = autoShadingCfg.find(AZIMUTH_ELEMENT_NAME)
                    Blinds[blindID].param.autoShading.observer.azimuthRangeNorth = float(cfgItem.attrib['rangenorth'])
                    Blinds[blindID].param.autoShading.observer.azimuthRangeSouth = float(cfgItem.attrib['rangesouth'])

                #initialize time control
                timeControlCfg = blindCfg.find('.//parameters/timecontrol')
                if timeControlCfg != None:
                    enableCfg = timeControlCfg.find(ENABLE_ELEMENT_NAME)
                    #get mapped PDI process tag: <processtag>light1TimeEnable</processtag>
                    processTag = enableCfg.find(PROCESSTAG_ELEMENT_NAME)                 
                    #each IOsignal has an addProcessTag function: call it for enable
                    ioSignalInst = getattr(Blinds[blindID].param.timecontrol, ENABLE_ELEMENT_NAME)              #get access to IO signal: "enable"
                    ioSignalInst.addProcessTag(processTag.text, None)                    
                
                    #analyze all event
                    eventCfg = blindCfg.find('.//parameters/timecontrol/events')
                    eventList = eventCfg.findall(EVENT_ELEMENT_NAME)
                    for event in eventList:
                        #add this event to the switch
                        Blinds[blindID].param.timecontrol.eventList.append(calEvent())
                        #access its event configuration and apply it to recently (-1) appended object
                        Blinds[blindID].param.timecontrol.eventList[-1].action = event.attrib['action']
                        Blinds[blindID].param.timecontrol.eventList[-1].triggerHour = int(event.attrib['hour'])
                        Blinds[blindID].param.timecontrol.eventList[-1].triggerMinute = int(event.attrib['minute'])
                
                        #get restriction in days and days of week
                        dateRangeCfg = event.find(DATERANGES_ELEMENT_NAME)
                        dateRangeList = dateRangeCfg.findall(DATERANGE_ELEMENT_NAME)
                        for dateRange in dateRangeList:
                            #add date range
                            Blinds[blindID].param.timecontrol.eventList[-1].dateRangeList.append(calEventDateRange())
                            
                            #get range in days
                            startDate = dateRange.find(START_ELEMENT_NAME)
                            endDate = dateRange.find(END_ELEMENT_NAME)
                            #convert both dates into a day of year index of the current year for further processing
                            Blinds[blindID].param.timecontrol.eventList[-1].dateRangeList[-1].startDayIndex = datetime.date(datetime.datetime.now().year, int(startDate.attrib['month']), int(startDate.attrib['day'])).timetuple().tm_yday
                            Blinds[blindID].param.timecontrol.eventList[-1].dateRangeList[-1].endDayIndex = datetime.date(datetime.datetime.now().year, int(endDate.attrib['month']), int(endDate.attrib['day'])).timetuple().tm_yday
                            
                            #get valid days of week where event has to be executed
                            weekDayCfg = dateRange.find(WEEKDAYS_ELEMENT_NAME)
                            weekDaysList = weekDayCfg.findall(WEEKDAY_ELEMENT_NAME)
                            for weekDay in weekDaysList:
                                Blinds[blindID].param.timecontrol.eventList[-1].dateRangeList[-1].weekDayList.append(int(weekDay.text))


                #initialize status points
                ioNameList = getClassAttributes(Blinds[blindID].status)      #['stopped', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    statusCfg = blindCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Blinds[blindID].status, ioName)              #get access to IO signal: "ontime", "energy",...
                            ioSignalInst.addProcessTag(processTag.text, None)

            except Exception, e:
                print("Loading configuration for blind <{0}> failed: {1}".format(blindID, e))
                return    

        #read configuration of group control
        for groupCfg in cfgRoot.findall(GROUP_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                groupID = groupCfg.get('id')
                ControlGroups[groupID] = controlGroupManager(PDI)
                ControlGroups[groupID].groupID = groupID
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(ControlGroups[groupID].inputs)      #['open', 'close',...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="on">
                    inputCfg = groupCfg.find('.//inputs/input[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(ControlGroups[groupID].inputs, ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(ControlGroups[groupID].outputs)      #['open', 'close', 'teach']
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = groupCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(ControlGroups[groupID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)


            except Exception, e:
                print("Loading configuration for group <{0}> failed: {1}".format(groupID, e))
                return    


    except Exception, e:
        print("Loading module configuration <{0}> for blinds and shading failed: {1}".format(MODULE_CFG_FILE_NAME,e))
        return


def update(PDI):
    global Blinds
    global ControlGroups

    #handle all groups to control several blinds at once
    for group in ControlGroups:
        ControlGroups[group].update(PDI)

    #handle all blinds
    for blind in Blinds:
        Blinds[blind].update(PDI)

        
class blindManager:
    "Control of blinds and shutters"

    '''
    Functional description
    Can be operated manually: open/close/stop and to a certain position (set pos + cmd)
    Emergency override allows closing (blinds) and shutting (shutters) in case of bad weather and storm
    The position will be calculated internally
    A manual operation with an external switch will rest internally calculated position and resets auto shading mode
    Supports auto shading: 
        Automatic positioning based on sun position
        Only active if enabled and the internal position is valid and they are not closed (this mode won't open the shutters)
        Active but suspended if it is cloudy
        Loosing the position or stop operation will disable auto shading mode
        Open/close can either be triggered by date, time, weekday or sunrise or sunset 
    '''

   
    #init
    def __init__(self, PDI):
        self.blindID = None
        self.inputs = deviceInputs(PDI)
        self.outputs = deviceOutputs(PDI)
        self.param = deviceParameters(PDI)
        self.status = deviceStatus(PDI)
        self.oldMinute = datetime.datetime.now().minute
        self.newMinuteAutoShading = False
        self.newMinuteTimeControl = False
        
        self.openAtSunrise = False
        self.closeAtSunset = False
        self.sunriseTime = 0
        self.sunsetTime = 0
        self.yahaHome = core.modules.astral.Location(info=None)
        
        self.blindPosLin = xyLin()
        self.blindStopRamp = 0
        self.motorPosInterpolation = motorPosInterpolation(VALID_POS_TIMEOUT, FULLY_OPEN_POS, FULLY_CLOSED_POS)


        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sMOVE_OPEN": self.sMOVE_OPEN,
                             "sMOVE_OPEN_RESET": self.sMOVE_OPEN_RESET,
                             "sMOVE_CLOSE": self.sMOVE_CLOSE,
                             "sMOVE_CLOSE_RESET": self.sMOVE_CLOSE_RESET,
                             "sMOVE_STOP": self.sMOVE_STOP,
                             "sMOVE_STOP_RESET": self.sMOVE_STOP_RESET,
                             "sTIME": self.sTIME,
                             "sMOVE_POSITION_INIT": self.sMOVE_POSITION_INIT,
                             "sMOVE_POSITION_CLOSING": self.sMOVE_POSITION_CLOSING,
                             "sMOVE_POSITION_OPENING": self.sMOVE_POSITION_OPENING,
                             "sAUTO_SHADING_INIT": self.sAUTO_SHADING_INIT,
                             "sAUTO_SHADING_CHECK_SUN_IN_RANGE": self.sAUTO_SHADING_CHECK_SUN_IN_RANGE,
                             "sAUTO_SHADING_BLIND_MOVEMENT_INIT": self.sAUTO_SHADING_BLIND_MOVEMENT_INIT,
                             "sAUTO_SHADING_BLIND_MOVEMENT_OPENING": self.sAUTO_SHADING_BLIND_MOVEMENT_OPENING,
                             "sAUTO_SHADING_BLIND_MOVEMENT_CLOSING": self.sAUTO_SHADING_BLIND_MOVEMENT_CLOSING,
                             "sTIME": self.sTIME,
                             "sTEACH_START": self.sTEACH_START,
                             "sTEACH_END": self.sTEACH_END
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""




    #cyclic logic    
    def update(self, PDI):
        if (self.oldMinute != datetime.datetime.now().minute):
            self.oldMinute = datetime.datetime.now().minute
            self.newMinuteAutoShading = True
            self.newMinuteTimeControl = True
            
        #execute state machine
        self.statemachine[self.activeState]()
        #logging of state
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Blind <{0}> state: {1}".format(self.blindID, self.activeState))
        
        '''
        Stop Rampe dynamisch rechnen
        Badezimmer Blind positionen ausmessen und korrekt konfigurieren
        '''        
        
        #interpolate motor position between two consecutive I/O updates
        #actmotorposition    ...motor position from sensor 
        #calcmotorposition   ...interpolation of motor position
        #actblindposition    ...calculated blind position
        self.motorPosInterpolation.interpolation(self.status.actmotorposition.value(), self.status.opening.value(), self.status.closing.value(), self.status.stopped.value())


        #use interpolated values if available
        if (self.motorPosInterpolation.isValid == True):
            self.status.calcmotorposition.value(self.motorPosInterpolation.calcMotorPos)
            self.blindStopRamp = self.blindPosLin.calcYfromX( self.motorPosInterpolation.vMotor * self.param.window.motorStopDelay )
            #print(self.blindStopRamp)
        #in case interpolation is not valid use last received motor position to calculate blind posistion
        else:
            self.status.calcmotorposition.value(self.status.actmotorposition.value())
        
        #calculate blind position from motor position
        self.status.actblindposition.value( self.blindPosLin.calcYfromX(self.status.calcmotorposition.value()) )    


        #update astronomical data
        #http://www.timeanddate.com/sun/austria/salzburg
        #https://pysolar.readthedocs.org/en/latest/
        self.yahaHome.latitude = self.inputs.homelatitude.value()
        self.yahaHome.longitude = self.inputs.homelongitude.value()
        self.yahaHome.elevation = self.inputs.homeelevation.value()
        self.yahaHome.timezone = self.inputs.hometimezone.value()
        self.yahaHome.solar_depression = 'civil'
    
 
    def sIDLE(self):
        #check for stop (has overall priority)
        if self.inputs.stop.value() == 1:
            self.inputs.stop.value(0)
            self.activeState = "sMOVE_STOP"
            
        elif self.inputs.open.value() == 1:
            self.inputs.open.value(0)
            self.activeState = "sMOVE_OPEN"
        
        elif self.inputs.close.value() == 1:
            self.inputs.close.value(0)
            self.activeState = "sMOVE_CLOSE"
        
        elif self.inputs.teach.value() == 1:
            self.inputs.teach.value(0)
            self.activeState = "sTEACH_START"

        elif (self.inputs.cmdStartMovePosition.value() == 1):
            self.inputs.cmdStartMovePosition.value(0)
            self.activeState = "sMOVE_POSITION_INIT"

        #evaluate every minute to recalculate position
        elif (self.newMinuteAutoShading == True):
            self.newMinuteAutoShading = False
            #activate auto shading if enabled and not fully closed (opening needs to be done by event or manually: a fully shut shutter never opens automatically)
            if (self.param.autoShading.enable.value() == 1) and (self.status.fullyclosed.value() == 0):
                self.activeState = "sAUTO_SHADING_INIT"

        #evaluate every minute whether an event is active
        elif (self.newMinuteTimeControl == True):
            self.newMinuteTimeControl = False
                
            if (self.param.timecontrol.enable.value() == 1):
                self.activeState = "sTIME"

    
    def sMOVE_OPEN(self):
        self.outputs.open.value(1)
        self.activeState = "sMOVE_OPEN_RESET"
    
    def sMOVE_OPEN_RESET(self):
        self.outputs.open.value(0)
        self.activeState = "sIDLE"
    
    def sMOVE_CLOSE(self):
        self.outputs.close.value(1)
        self.activeState = "sMOVE_CLOSE_RESET"
    
    def sMOVE_CLOSE_RESET(self):
        self.outputs.close.value(0)
        self.activeState = "sIDLE"
    
    def sMOVE_STOP(self):
        self.outputs.stop.value(1)
        self.activeState = "sMOVE_STOP_RESET"
    
    def sMOVE_STOP_RESET(self):
        self.outputs.stop.value(0)
        self.activeState = "sIDLE"

    def sMOVE_POSITION_INIT(self):
        #decide which direction
        if (float(self.inputs.setblindposition.value()) > float(self.status.actblindposition.value())):
            #override: if set position of blind is set to 100% (fully closed) close completely (necessary due to linearization)
            if (self.inputs.setblindposition.value() == 100):
                self.activeState = "sMOVE_CLOSE"
            else:
                self.outputs.close.value(1)
                self.activeState = "sMOVE_POSITION_CLOSING"
        else:
            #override: if set position of blind is set to 0% (fully open) open completely (necessary due to linearization)
            if (self.inputs.setblindposition.value() == 0):
                self.activeState = "sMOVE_OPEN"
            else:
                self.outputs.open.value(1)
                self.activeState = "sMOVE_POSITION_OPENING"

            
        
    def sMOVE_POSITION_CLOSING(self):
        self.outputs.close.value(0)
        
        #stop position mode if operator stops blind
        if (self.inputs.stop.value() == 1):
            self.activeState = "sMOVE_STOP"

        #wait until position has been reached
        if (float(self.status.actblindposition.value()) + self.blindStopRamp >= float(self.inputs.setblindposition.value())):
            self.activeState = "sMOVE_STOP"

    def sMOVE_POSITION_OPENING(self):
        self.outputs.open.value(0)

        #stop position mode if operator stops blind
        if (self.inputs.stop.value() == 1):
            self.activeState = "sMOVE_STOP"

        #wait until position has been reached
        if (self.status.actblindposition.value() - self.blindStopRamp <= self.inputs.setblindposition.value()):
            self.activeState = "sMOVE_STOP"
        
    def sAUTO_SHADING_INIT(self):
        self.activeState = "sAUTO_SHADING_CHECK_SUN_IN_RANGE"
            
    def sAUTO_SHADING_CHECK_SUN_IN_RANGE(self):
        sunriseTime = self.yahaHome.sunrise(date=None, local=True)
        sunsetTime = self.yahaHome.sunset(date=None, local=True)
        sunAzimuth = self.yahaHome.solar_azimuth(dateandtime=None)
        print("Azimuth of sun: %s"%(sunAzimuth))

        #continue only if sun is risen already and not yet set and sun is in the range of the window
        curTimeInMinutes = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
        sunriseTimeInMinutes = sunriseTime.hour * 60 + sunriseTime.minute
        sunsetTimeInMinutes = sunsetTime.hour * 60 + sunsetTime.minute
        
        if (curTimeInMinutes > sunriseTimeInMinutes) and (curTimeInMinutes < sunsetTimeInMinutes) and \
           self.sunIsInRange(self.param.window.orientation, 
                             self.param.autoShading.observer.azimuthRangeNorth, 
                             self.param.autoShading.observer.azimuthRangeSouth):
        
            self.activeState = "sAUTO_SHADING_BLIND_MOVEMENT_INIT"
        else:
            self.activeState = "sIDLE"
            
        
    def sAUTO_SHADING_BLIND_MOVEMENT_INIT(self):
        sunElevation = self.yahaHome.solar_elevation(dateandtime=None)
        print("Elevation of sun: {0}".format(sunElevation))
        
        #calculate distance of blind to block the sun
        h_sow = self.param.autoShading.observer.windowDistance * math.tan(math.radians(sunElevation))
        print ("h_sow: {0}".format(h_sow))
        
        l_b = max(min((self.param.window.floorDistance + self.param.window.height - self.param.autoShading.observer.height - h_sow), self.param.window.height), 0)
        print ("l_b: {0}".format(l_b))

        l_b100 = FULLY_CLOSED_POS / self.param.window.height * l_b
        print ("l_b100: {0}".format(l_b100))

        #only move blind if new position is at least start / stop ramp distance away to avoid micro movements were motor can not be stopped in time 
        if abs(self.param.autoShading.setPosition - l_b100) >= (self.blindStopRamp * 2):
            #set new set position                
            self.param.autoShading.setPosition = l_b100

            if (l_b100 >= self.param.autoShading.setPosition):
                self.activeState = "sAUTO_SHADING_BLIND_MOVEMENT_CLOSING"
                self.outputs.close.value(1)
            else:
                self.activeState = "sAUTO_SHADING_BLIND_MOVEMENT_OPENING"
                self.outputs.open.value(1)

        else:
            print("new blind set position not far enough away. Min: {0}".format(self.blindStopRamp * 2))
            self.activeState = "sIDLE"
            

    def sAUTO_SHADING_BLIND_MOVEMENT_OPENING(self):
        self.outputs.open.value(0)
        
        #stop auto shading if user stops
        if (self.inputs.stop.value() == 1):
            self.param.autoShading.enable.value(0)    #disable auto shading
            self.activeState = "sMOVE_STOP"
            return

        #wait until position has been reached
        if (self.status.actblindposition.value() - self.blindStopRamp <= self.param.autoShading.setPosition):
            self.activeState = "sMOVE_STOP"
            return

    def sAUTO_SHADING_BLIND_MOVEMENT_CLOSING(self):
        self.outputs.close.value(0)

        #stop auto shading if user stops
        if (self.inputs.stop.value() == 1):
            self.param.autoShading.enable.value(0)    #disable auto shading
            self.activeState = "sMOVE_STOP"
            return

        #wait until position has been reached
        if (float(self.status.actblindposition.value()) + self.blindStopRamp >= self.param.autoShading.setPosition):
            self.activeState = "sMOVE_STOP"
            return


    def sTIME(self):
        #evaluate all events whether there is an action to perform
        for event in self.param.timecontrol.eventList:
            calAction = event.getAction(datetime.datetime.now())
            if (calAction == EVENT_ACTION_OPEN):
                self.activeState = "sMOVE_OPEN"
                return
            
            elif (calAction == EVENT_ACTION_CLOSE):
                self.activeState = "sMOVE_CLOSE"
                return
        
            elif (calAction == EVENT_ACTION_OPEN_AT_SUNRISE):
                self.sunriseTime = self.yahaHome.sunrise(date=None, local=True)
                #remove time zone for later comparison with now()
                self.sunriseTime = datetime.datetime(self.sunriseTime.year, self.sunriseTime.month, self.sunriseTime.day, self.sunriseTime.hour, self.sunriseTime.minute, self.sunriseTime.second)
                self.openAtSunrise = True
        
            elif (calAction == EVENT_ACTION_CLOSE_AT_SUNSET):
                self.sunsetTime = self.yahaHome.sunset(date=None, local=True)
                #remove time zone for later comparison with now()
                self.sunsetTime = datetime.datetime(self.sunsetTime.year, self.sunsetTime.month, self.sunsetTime.day, self.sunsetTime.hour, self.sunsetTime.minute, self.sunsetTime.second)
                self.closeAtSunset = True
        
        #processing possible set sunrise/sunset flags
        if (self.openAtSunrise == True) and (datetime.datetime.now() >= self.sunriseTime):
            self.openAtSunrise = False
            self.activeState = "sMOVE_OPEN"
            return
        
        elif (self.closeAtSunset == True) and (datetime.datetime.now() >= self.sunsetTime):
            self.closeAtSunset = False
            self.activeState = "sMOVE_CLOSE"
            return
            
            
        self.activeState = "sIDLE"
        return

    
    def sTEACH_START(self):
        self.outputs.teach.value(1)
        self.activeState = "sTEACH_END"
        return
    
    def sTEACH_END(self):
        self.outputs.teach.value(0) #reset teach command to avoid continous teaching
        self.activeState = "sIDLE"
        return
    

    def sunIsInRange(self, windowOrientation, northRange, southRange):
        sunAzimuth = self.yahaHome.solar_azimuth(dateandtime=None)

        if (sunAzimuth >= windowOrientation - northRange) and (sunAzimuth <= windowOrientation + southRange):
            return True
            print("sunIsInRange: true")
        else:
            print("sunIsInRange: false")
            return False

class deviceInputs():
    'Collection of inputs of a certain device'
    #init
    def __init__(self, PDI):
        self.open = core.modules.iosignal.IOsignal(PDI)
        self.close = core.modules.iosignal.IOsignal(PDI)
        self.setblindposition = core.modules.iosignal.IOsignal(PDI)
        self.cmdStartMovePosition = core.modules.iosignal.IOsignal(PDI)
        self.stop = core.modules.iosignal.IOsignal(PDI)
        self.angle = core.modules.iosignal.IOsignal(PDI)
        self.teach = core.modules.iosignal.IOsignal(PDI)
        self.manualswitch = core.modules.iosignal.IOsignal(PDI)
        self.iscloudy = core.modules.iosignal.IOsignal(PDI)
        self.homelatitude = core.modules.iosignal.IOsignal(PDI)
        self.homelongitude = core.modules.iosignal.IOsignal(PDI)
        self.homeelevation = core.modules.iosignal.IOsignal(PDI)
        self.hometimezone = core.modules.iosignal.IOsignal(PDI)



class deviceOutputs():
    'Collection of outputs of a certain device'
    #init
    def __init__(self, PDI):
        self.open = core.modules.iosignal.IOsignal(PDI)
        self.close = core.modules.iosignal.IOsignal(PDI)
        self.stop = core.modules.iosignal.IOsignal(PDI)
        self.teach = core.modules.iosignal.IOsignal(PDI)

class deviceParameters:
    #init
    def __init__(self, PDI):
        self.window = paramWindow()
        self.autoShading = paramAutoShading(PDI)
        self.timecontrol = paramTimeControl(PDI)
   

class paramWindow:
    #init
    def __init__(self):
        self.orientation = 0        #degree to north    
        self.height = 0             #height of window in m
        self.floorDistance = 0      #distance from floor to bottom border of window
        self.motorPosFullyOpen = 0  #position of motor when blind is fully open
        self.motorPosFullyClosed = 0  #position of motor when the blind touches the windows sims
        self.motorStopDelay = 0     #movement until motor is fully stopped
        
class paramAutoShading:
    #init
    def __init__(self, PDI):
        self.enable = core.modules.iosignal.IOsignal(PDI)   
        self.observer = paramAutoShadingObserver()
        self.setPosition = 0

class paramAutoShadingObserver:
    #init
    #this defines the position where above this point the blind will protect from the sun
    def __init__(self):
        self.height = 0     #height of observer relative to floor 
        self.windowDistance = 0     #distance of observer from the window
        self.azimuthRangeNorth = 0  #North and south build the band in which auto shading is active        
        self.azimuthRangeSouth = 0  #North and south build the band in which auto shading is active        

class paramTimeControl():
    #init
    def __init__(self, PDI):
        self.enable = core.modules.iosignal.IOsignal(PDI)
        self.eventList = []

class deviceStatus:
    #init
    def __init__(self, PDI):
        self.stopped = core.modules.iosignal.IOsignal(PDI);
        self.opening = core.modules.iosignal.IOsignal(PDI);
        self.closing = core.modules.iosignal.IOsignal(PDI);
        self.fullyopen = core.modules.iosignal.IOsignal(PDI);
        self.fullyclosed = core.modules.iosignal.IOsignal(PDI);
        self.calcmotorposition = core.modules.iosignal.IOsignal(PDI);
        self.actmotorposition = core.modules.iosignal.IOsignal(PDI);
        self.actblindposition = core.modules.iosignal.IOsignal(PDI);
        self.error = core.modules.iosignal.IOsignal(PDI);

class xyLin():
    #init
    def __init__(self):
        self.x1 = 0         #motor axis
        self.x2 = 0
        self.y1 = 0         #blind axis
        self.y2 = 0
        self.k = 0
        self.d = 0
        self.xMin = 0
        self.xMax = 0
        self.yMin = 0
        self.yMax = 0
    
    def calcK(self):
        try:
            self.k = (float(self.y2) - float(self.y1)) / (float(self.x2) - float(self.x1)) 
        except:
            self.k = 0

    def calcD(self):
        try:
            self.d = ( (float(self.y1) * float(self.x2)) - (float(self.y2) * float(self.x1)) ) / (float(self.x2) - float(self.x1))
        except:
            self.d = 0
        
    def calcYfromX(self, x):
        try:
            y = self.k * float(x) + self.d #y = kx + d
            return max(min(y, self.yMax), self.yMin)
        except:
            return 0
    
    def calcXfromY(self, y):
        try:
            x = (y - self.d) / self.k     #x = (y - d) / k
            return max(min(x, self.xMax), self.xMin)
        except:
            return 0
    
class motorPosInterpolation():
    #init
    def __init__(self, timeout, min, max):
        self.timeout = timeout
        self.motorPosMin = min
        self.motorPosMax = max
        
        self.isValid = False
        self.calcMotorPos = 0
        self.lastActMotorPos = motorPosSample()
        self.motorPosTrace = list()
        self.vMotor = 0
        
    def interpolation(self, newActMotorPos, opening, closing, stopped):
        #check whether a new position value was sent by the sensor => indicates a movement
        if (stopped == 1):
            #empty traced position because the time between two samples can not be used to calculate motor velocity
            del self.motorPosTrace[:]
            self.lastActMotorPos.position = float(newActMotorPos)
            self.lastActMotorPos.timeStamp = time.time()

        if (newActMotorPos != self.lastActMotorPos.position):
            #print("Delta of interpolation: {0}".format(self.calcMotorPos - float(newActMotorPos)))
            #save new actual position as last known measured position
            self.lastActMotorPos.position = float(newActMotorPos)
            self.lastActMotorPos.timeStamp = time.time()
            
            #set calculated position to current measured position. From this position on the interpolation will start
            self.calcMotorPos = self.lastActMotorPos.position
            
            #update trace buffer
            self.motorPosTrace.append(motorPosSample())
            self.motorPosTrace[-1].position = self.lastActMotorPos.position
            self.motorPosTrace[-1].timeStamp = self.lastActMotorPos.timeStamp


            #as soon as two elements are in the trace buffer an speed calculation is possible. Remove all oldest elements
            if (len(self.motorPosTrace) >= 2):
                del self.motorPosTrace[0:len(self.motorPosTrace)-2]
                #calculate velocity of motor
                try:
                    self.vMotor = abs(self.motorPosTrace[0].position - self.motorPosTrace[1].position) / abs(self.motorPosTrace[0].timeStamp - self.motorPosTrace[1].timeStamp)
                    self.isValid = True
                except:
                    self.vMotor = 0
                    del self.motorPosTrace[:]      #clear trace because it was obviously not possible to calculate a velocity from it
                    self.isValid = False

        #interpolation only starts if vMotor has been calculated
        if (self.isValid == True):
            if (opening == 1):
                #calculate motor position based last measured position and adjust it depending on speed and elapsed time 
                self.calcMotorPos = self.lastActMotorPos.position - self.vMotor * (time.time() - self.lastActMotorPos.timeStamp)
                #limit calculation to min/max
                self.calcMotorPos = max(min(self.calcMotorPos, self.motorPosMax), self.motorPosMin)
    
            if (closing == 1):
                #calculate motor position based last measured position and adjust it depending on speed and elapsed time 
                self.calcMotorPos = self.lastActMotorPos.position + self.vMotor * (time.time() - self.lastActMotorPos.timeStamp)
                #limit calculation to min/max
                self.calcMotorPos = max(min(self.calcMotorPos, self.motorPosMax), self.motorPosMin)
        #if interpolation is valid use last measured position as calculated position
        else:
           self.calcMotorPos = newActMotorPos 

class motorPosSample():
    def __init__(self):
        self.position = 0
        self.timeStamp = None
    
class controlGroupManager:
    "Controls groups of blinds"
   
    #init
    def __init__(self, PDI):
        self.groupID = None
        self.inputs = groupInputs(PDI)
        self.outputs = groupOutputs(PDI)

        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sMOVE_OPEN": self.sMOVE_OPEN,
                             "sMOVE_OPEN_WAIT": self.sMOVE_OPEN_WAIT,
                             "sMOVE_OPEN_RESET": self.sMOVE_OPEN_RESET,
                             "sMOVE_CLOSE": self.sMOVE_CLOSE,
                             "sMOVE_CLOSE_WAIT": self.sMOVE_CLOSE_WAIT,
                             "sMOVE_CLOSE_RESET": self.sMOVE_CLOSE_RESET,
                             "sMOVE_STOP": self.sMOVE_STOP,
                             "sMOVE_STOP_WAIT": self.sMOVE_STOP_WAIT,
                             "sMOVE_STOP_RESET": self.sMOVE_STOP_RESET,
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""




    #cyclic logic    
    def update(self, PDI):
        #execute state machine
        self.statemachine[self.activeState]()
        #logging of state
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Group <{0}> state: {1}".format(self.groupID, self.activeState))


    def sIDLE(self):
        #check for stop (has overall priority)
        if self.inputs.stop.value() == 1:
            self.inputs.stop.value(0)
            self.activeState = "sMOVE_STOP"
            
        elif self.inputs.open.value() == 1:
            self.inputs.open.value(0)
            self.activeState = "sMOVE_OPEN"
        
        elif self.inputs.close.value() == 1:
            self.inputs.close.value(0)
            self.activeState = "sMOVE_CLOSE"


    def sMOVE_OPEN(self):
        self.outputs.open.value(1)
        self.activeState = "sMOVE_OPEN_WAIT"

    def sMOVE_OPEN_WAIT(self):
        self.activeState = "sMOVE_OPEN_RESET"
    
    def sMOVE_OPEN_RESET(self):
        self.outputs.open.value(0)
        self.activeState = "sIDLE"
    
    def sMOVE_CLOSE(self):
        self.outputs.close.value(1)
        self.activeState = "sMOVE_CLOSE_WAIT"
    
    def sMOVE_CLOSE_WAIT(self):
        self.activeState = "sMOVE_CLOSE_RESET"
    
    def sMOVE_CLOSE_RESET(self):
        self.outputs.close.value(0)
        self.activeState = "sIDLE"
    
    def sMOVE_STOP(self):
        self.outputs.stop.value(1)
        self.activeState = "sMOVE_STOP_WAIT"
    
    def sMOVE_STOP_WAIT(self):
        self.activeState = "sMOVE_STOP_RESET"
    
    def sMOVE_STOP_RESET(self):
        self.outputs.stop.value(0)
        self.activeState = "sIDLE"





class groupInputs():
    'Collection of inputs of a certain device'
    #init
    def __init__(self, PDI):
        self.open = core.modules.iosignal.IOsignal(PDI)
        self.close = core.modules.iosignal.IOsignal(PDI)
        self.stop = core.modules.iosignal.IOsignal(PDI)


class groupOutputs():
    'Collection of outputs of a certain device'
    #init
    def __init__(self, PDI):
        self.open = core.modules.iosignal.IOsignal(PDI)
        self.close = core.modules.iosignal.IOsignal(PDI)
        self.stop = core.modules.iosignal.IOsignal(PDI)




#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    
 