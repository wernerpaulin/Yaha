#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py


MODULE_CFG_FILE_NAME = "module.cfg.xml"
BLIND_CFG_ELEMENT_NAME = "./blinds/blind"
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
CLOSE_TIME_DURATION_ELEMENT_NAME = "closetime"
COVER_START_TIME_DURATION_ELEMENT_NAME = "coverstarttime"
TOUCH_DOWN_TIME_DURATION_ELEMENT_NAME = "touchdowntime"
MOTOR_STOP_DELAY_DURATION_ELEMENT_NAME = "motorstopdelay"
POSITION_ELEMENT_NAME = "position"
SIZE_ELEMENT_NAME = "size"
FULLY_OPEN_POS = 0
FULLY_CLOSED_POS = 100

import os
import xml.etree.ElementTree as xmlParser
import datetime, time

import core.modules.iosignal
from core.modules.cal_event import *

from core.modules.astral import Astral
from core.modules.pytz import all_timezones

def init(PDI):
    global Blinds
    Blinds = dict()
    ioList = []
    attrList = []    

    #read module configuration and initialize each device
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for blindCfg in cfgRoot.findall(BLIND_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                blindID = blindCfg.get('id')
                Blinds[blindID] = blindManager(PDI)
                
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
                    Blinds[blindID].param.window.relativeAltitude = float(cfgItem.attrib['relativealtitude'])

                    cfgItem = windowCfg.find(SIZE_ELEMENT_NAME)
                    Blinds[blindID].param.window.height = float(cfgItem.attrib['height'])

                    cfgItem = windowCfg.find(CLOSE_TIME_DURATION_ELEMENT_NAME)
                    Blinds[blindID].param.window.closeTimeDuration = float(cfgItem.attrib['duration'])

                    cfgItem = windowCfg.find(COVER_START_TIME_DURATION_ELEMENT_NAME)
                    Blinds[blindID].param.window.coverStartTimeDuration = float(cfgItem.attrib['duration'])

                    cfgItem = windowCfg.find(TOUCH_DOWN_TIME_DURATION_ELEMENT_NAME)
                    Blinds[blindID].param.window.touchDownTimeDuration = float(cfgItem.attrib['duration'])

                    cfgItem = windowCfg.find(MOTOR_STOP_DELAY_DURATION_ELEMENT_NAME)
                    Blinds[blindID].param.window.motorStopRamp = float(FULLY_CLOSED_POS) / float(Blinds[blindID].param.window.closeTimeDuration) * float(cfgItem.attrib['duration'])

                    #initialize blind/motor linearization (all parameters are normalized to 0..100
                    Blinds[blindID].blindPosLin.x1 = float(FULLY_CLOSED_POS) / float(Blinds[blindID].param.window.closeTimeDuration) * Blinds[blindID].param.window.coverStartTimeDuration
                    Blinds[blindID].blindPosLin.x2 = float(FULLY_CLOSED_POS) / float(Blinds[blindID].param.window.closeTimeDuration) * Blinds[blindID].param.window.touchDownTimeDuration
                    Blinds[blindID].blindPosLin.y1 = FULLY_OPEN_POS
                    Blinds[blindID].blindPosLin.y2 = FULLY_CLOSED_POS

                    Blinds[blindID].blindPosLin.xMin = FULLY_OPEN_POS
                    Blinds[blindID].blindPosLin.xMax = FULLY_CLOSED_POS
                    Blinds[blindID].blindPosLin.yMin = FULLY_OPEN_POS
                    Blinds[blindID].blindPosLin.yMax = FULLY_CLOSED_POS

                    Blinds[blindID].blindPosLin.calcK()
                    Blinds[blindID].blindPosLin.calcD()

                #initialize anti glare
                antiGlareCfg = blindCfg.find('.//parameters/antiglare')
                #continue only if configuration exists
                if antiGlareCfg != None:
                    #link enable signal with PDI
                    enableCfg = antiGlareCfg.find(ENABLE_ELEMENT_NAME)
                    #get mapped PDI process tag: <processtag>xxx</processtag>
                    processTag = enableCfg.find(PROCESSTAG_ELEMENT_NAME)                 
                    #each IOsignal has an addProcessTag function: call it generically depending on ioName
                    ioSignalInst = getattr(Blinds[blindID].param.antiGlare, ENABLE_ELEMENT_NAME)
                    ioSignalInst.addProcessTag(processTag.text, None)                    

                    #set minimum brightness
                    Blinds[blindID].param.antiGlare.minBrightness = float(antiGlareCfg.attrib['minbrightness'])


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
                print('Loading configuration for blind <%s> failed: %s'%(e, blindID))
                return    

    except Exception, e:
        print('Loading blinds module configuration failed: %s'%(e))
        return


def update(PDI):
    global Blinds

    for blind in Blinds:
        Blinds[blind].update(PDI)
        
class blindManager:
    "Control of blinds and shutters"

    '''
    Functional description
    Can be operated manually: open/close/stop and to a certain position (set pos + cmd)
    Emergency override allows closing (blinds) and shutting (shutters) in case of bad weather and storm
    The position will be calculated internally, homing is done automatically in one of the end positions
    A manual operation with an external switch will rest internally calculated position and resets anti glare mode
    Supports anti-glare mode: 
        Automatic positioning based on brightness and sun position
        Only active if enabled, minimum brightness (no clouds), the internal position is valid and they are not closed (this mode won't open the shutters)
        Automatic homing if blinds are open but not yet homed (opening movement)
        Loosing the position or stop operation will disable anti-glare mode
        Open/close can either be triggered by date, time, weekday or sunrise or sunset 
    '''

   
    #init
    def __init__(self, PDI):
        self.inputs = deviceInputs(PDI)
        self.outputs = deviceOutputs(PDI)
        self.param = deviceParameters(PDI)
        self.status = deviceStatus(PDI)
        self.oldMinute = datetime.datetime.now().minute
        self.oldAntiGlareEnable = 0
        self.newMinuteAntiGlare = False
        self.newMinuteTimeControl = False
        
        self.homingValid = False
        self.isMovingOpen = False
        self.isMovingClose = False
        self.moveStartTime = 0
        self.lastCallTime = 0
        self.elapsedTime = 0
        self.posInc = 0
        self.openAtSunrise = False
        self.closeAtSunset = False
        self.sunriseTime = 0
        self.sunsetTime = 0
        self.yahaHome = core.modules.astral.Location(info=None)
        
        self.blindPosLin = blindPosLin()


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
                             "sANTI_GLARE_INIT": self.sANTI_GLARE_INIT,
                             "sANTI_GLARE_HOMING_OPEN": self.sANTI_GLARE_HOMING_OPEN,
                             "sANTI_GLARE_HOMING_OPEN_RESET": self.sANTI_GLARE_HOMING_OPEN_RESET,
                             "sANTI_GLARE_WAIT_HOMING_VALID": self.sANTI_GLARE_WAIT_HOMING_VALID,
                             "sANTI_GLARE_CHECK_SUN_IN_RANGE": self.sANTI_GLARE_CHECK_SUN_IN_RANGE,
                             "sANTI_GLARE_BLIND_MOVEMENT_INIT": self.sANTI_GLARE_BLIND_MOVEMENT_INIT,
                             "sANTI_GLARE_BLIND_MOVEMENT_OPENING": self.sANTI_GLARE_BLIND_MOVEMENT_OPENING,
                             "sANTI_GLARE_BLIND_MOVEMENT_CLOSING": self.sANTI_GLARE_BLIND_MOVEMENT_CLOSING,
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
            self.newMinuteAntiGlare = True
            self.newMinuteTimeControl = True
            
        #execute state machine
        self.statemachine[self.activeState]()
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Blind state: " + self.activeState)
        
        #get time since last update to calculate position increment
        self.elapsedTime = time.time() - self.lastCallTime
        self.lastCallTime = time.time()

        #reset homing if someone changed the system time
        if (self.elapsedTime < 0) and (self.elapsedTime > self.param.window.closeTimeDuration):
            print("Blind: reset of homing - plausibility check of elapsed time failed")
            self.homingValid = False
        
        #homing of blind in end positions
        if (self.status.fullyclosed.value() == 1):
            self.homingValid = True
            self.status.calcmotorposition.value(FULLY_CLOSED_POS)

        elif (self.status.fullyopen.value() == 1):
            self.homingValid = True
            self.status.calcmotorposition.value(FULLY_OPEN_POS)
        
        #reset homing as soon as someone operated the blind with an external switch
        if (self.inputs.manualswitch.value() == 1):
            print("Blind: reset of homing - manual switch operation")
            self.homingValid = False
            self.param.antiGlare.enable.value(0)
        
        #only calculated current position if homing is valid
        if (self.homingValid == True):
            #calculate position increment since last update cycle: if delta is negative or more then maximum close time => time has been changed => reset homing
            self.posInc = float(FULLY_CLOSED_POS) / float(self.param.window.closeTimeDuration) * float(self.elapsedTime)
            
            if (self.status.opening.value() == 1):
                self.status.calcmotorposition.value(self.status.calcmotorposition.value() - self.posInc)
                if (self.status.calcmotorposition.value() < FULLY_OPEN_POS):
                    self.status.calcmotorposition.value(FULLY_OPEN_POS)
                    
            elif (self.status.closing.value() == 1):
                self.status.calcmotorposition.value(float(self.status.calcmotorposition.value()) + float(self.posInc))
                if (self.status.calcmotorposition.value() > FULLY_CLOSED_POS):
                    self.status.calcmotorposition.value(FULLY_CLOSED_POS)
        else:
            #as long as homing is invalid use position from sensor - slow and occasionally updated but better then nothing
            self.status.calcmotorposition.value(self.status.actmotorposition.value())

        #calculate blind position from motor position
        self.status.actblindposition.value(self.blindPosLin.calcBlindPosFromMotorPos(self.status.calcmotorposition.value()))    

        #update astronomical data
        #http://www.timeanddate.com/sun/austria/salzburg
        #https://pysolar.readthedocs.org/en/latest/
        self.yahaHome.latitude = self.inputs.homelatitude.value()
        self.yahaHome.longitude = self.inputs.homelongitude.value()
        self.yahaHome.elevation = self.inputs.homeelevation.value()
        self.yahaHome.timezone = self.inputs.hometimezone.value()
        self.yahaHome.solar_depression = 'civil'
    
        #print(self.yahaHome.solar_azimuth(dateandtime=None))
        #print(self.yahaHome.solar_elevation(dateandtime=None))
        
 
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
            if (self.homingValid == True):
                self.activeState = "sMOVE_POSITION_INIT"
        
        #evaluate every minute to recalculate position
        elif (self.newMinuteAntiGlare == True):
            self.newMinuteAntiGlare = False
            #activate anti glare if enabled and not fully closed (opening needs to be done by event or manually: a fully shut shutter never opens automatically)
            if (self.param.antiGlare.enable.value() == 1) and (self.status.fullyclosed.value() == 0):
                self.activeState = "sANTI_GLARE_INIT"

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
        
        #stop position mode if homing has been lost or operator stops blind
        if (self.homingValid == False) or (self.inputs.stop.value() == 1):
            self.activeState = "sMOVE_STOP"

        #wait until position has been reached
        if (float(self.status.actblindposition.value()) + self.param.window.motorStopRamp >= float(self.inputs.setblindposition.value())):
            self.activeState = "sMOVE_STOP"

    def sMOVE_POSITION_OPENING(self):
        self.outputs.open.value(0)

        #stop position mode if homing has been lost or operator stops blind
        if (self.homingValid == False) or (self.inputs.stop.value() == 1):
            self.activeState = "sMOVE_STOP"

        #wait until position has been reached
        if (self.status.actblindposition.value() - self.param.window.motorStopRamp <= self.inputs.setblindposition.value()):
            self.activeState = "sMOVE_STOP"
        

    def sANTI_GLARE_INIT(self):
        #check if homing is valid, otherwise open shutter completely and close
        if (self.homingValid == True):
            self.activeState = "sANTI_GLARE_CHECK_SUN_IN_RANGE"
        else:
            self.activeState = "sANTI_GLARE_HOMING_OPEN"

    def sANTI_GLARE_HOMING_OPEN(self):
        self.outputs.open.value(1)
        self.activeState = "sANTI_GLARE_HOMING_OPEN_RESET"
    
    def sANTI_GLARE_HOMING_OPEN_RESET(self):
        self.outputs.open.value(0)
        self.activeState = "sANTI_GLARE_WAIT_HOMING_VALID"

    def sANTI_GLARE_WAIT_HOMING_VALID(self):
        #stop anti glare if user stops
        if (self.inputs.stop.value() == 1):
            self.param.antiGlare.enable.value(0)    #disable anti glare
            self.activeState = "sMOVE_STOP"
            return
        #continue with anti glare
        elif (self.homingValid == True):
            self.activeState = "sANTI_GLARE_CHECK_SUN_IN_RANGE"
            
    def sANTI_GLARE_CHECK_SUN_IN_RANGE(self):
        self.activeState = "sANTI_GLARE_BLIND_MOVEMENT_INIT"
        
    def sANTI_GLARE_BLIND_MOVEMENT_INIT(self):
        self.activeState = "sANTI_GLARE_BLIND_MOVEMENT_OPENING"

    def sANTI_GLARE_BLIND_MOVEMENT_OPENING(self):
        #stop anti glare if user stops or homing becomes invalid
        if (self.inputs.stop.value() == 1) or (self.homingValid == False):
            self.param.antiGlare.enable.value(0)    #disable anti glare
            self.activeState = "sMOVE_STOP"
            return

        self.activeState = "sMOVE_STOP"

    def sANTI_GLARE_BLIND_MOVEMENT_CLOSING(self):
        #stop anti glare if user stops or homing becomes invalid
        if (self.inputs.stop.value() == 1) or (self.homingValid == False):
            self.param.antiGlare.enable.value(0)    #disable anti glare
            self.activeState = "sMOVE_STOP"
            return
        
        self.activeState = "sMOVE_STOP"

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
                #remove timezone for later comparisson with now()
                self.sunriseTime = datetime.datetime(self.sunriseTime.year, self.sunriseTime.month, self.sunriseTime.day, self.sunriseTime.hour, self.sunriseTime.minute, self.sunriseTime.second)
                print(self.sunriseTime)
                self.openAtSunrise = True
        
            elif (calAction == EVENT_ACTION_CLOSE_AT_SUNSET):
                self.sunsetTime = self.yahaHome.sunset(date=None, local=True)
                #remove timezone for later comparisson with now()
                self.sunsetTime = datetime.datetime(self.sunsetTime.year, self.sunsetTime.month, self.sunsetTime.day, self.sunsetTime.hour, self.sunsetTime.minute, self.sunsetTime.second)
                print(self.sunsetTime)
                self.closeAtSunset = True
        
        #processing possible set sunrise/sunset flags
        if (self.openAtSunrise == True) and (datetime.datetime.now() >= self.sunriseTime):
            self.openAtSunrise = False
            print("openAtSunrise")
            self.activeState = "sMOVE_OPEN"
            return
        
        elif (self.closeAtSunset == True) and (datetime.datetime.now() >= self.sunsetTime):
            self.closeAtSunset = False
            print("closeAtSunset")
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
        self.emcyoverrideopen = core.modules.iosignal.IOsignal(PDI)
        self.emcyoverrideclose = core.modules.iosignal.IOsignal(PDI)
        self.ambientbrightness = core.modules.iosignal.IOsignal(PDI)
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
        self.antiGlare = paramAntiGlare(PDI)
        self.timecontrol = paramTimeControl(PDI)
   

class paramWindow:
    #init
    def __init__(self):
        self.orientation = 0        #degree to north    
        self.relativeAltitude = 0   #distance from ground to upper edge of window
        self.height = 0             #height of window in m
        self.closeTimeDuration = 0  #time the motor takes to fully shut the blind
        self.coverStartTimeDuration = 0 #time until the blind starts covering the window
        self.touchDownTimeDuration = 0 #time when the blind touches the windowsill
        self.motorStopRamp = 0      #movement distance until motor stops
        
class paramAntiGlare:
    #init
    def __init__(self, PDI):
        self.enable = core.modules.iosignal.IOsignal(PDI)    
        self.minBrightness = 0

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

class blindPosLin():
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
        
    def calcBlindPosFromMotorPos(self, motorPos):
        try:
            blindPos = self.k * float(motorPos) + self.d #y = kx + d
            return max(min(blindPos, self.yMax), self.yMin)
        except:
            return 0
    
    def calcMotorPosFromBlindPos(self, blindPos):
        try:
            motorPos = (blindPos - self.d) / self.k     #x = (y - d) / k
            return max(min(motorPos, self.xMax), self.xMin)
        except:
            return 0
    
    


#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    



''' DEBUGGING '''
if __name__ == "__main__":
    init(None)
                