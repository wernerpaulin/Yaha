#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py


import os
import datetime, time
import xml.etree.ElementTree as xmlParser

import core.modules.iosignal

import urllib2
import urllib
import re
import threading
import math

MODULE_CFG_FILE_NAME = "module.cfg.xml"
WS_CFG_ELEMENT_NAME = "./stations/station"

PROCESSTAG_ELEMENT_NAME = "processtag"
WSDATAITEM_ELEMENT_NAME = "wsdataitem"
HTTP_REQUEST_TIMEOUT = 15

VALUE_TYPE_REAL = "REAL"
VALUE_TYPE_TEXT = "TEXT"
VALUE_TYPE_TIME = "TIME"

WEATHER_CONDITION_SUNNY = 0
WEATHER_CONDITION_PARTLY_SUNNY = 1
WEATHER_CONDITION_CLOUDED = 2
WEATHER_CONDITION_RAIN = 3
WEATHER_CONDITION_SNOW = 4

THRESHOLD_ACT_TEMP_TREND = 0.2
THRESHOLD_REL_PRESSURE_TREND = 5
THRESHOLD_UV_INDEX_TREND = 1
THRESHOLD_HUMIDITY_TREND = 2

TREND_NO_CHANGE = 0
TREND_UP = 1
TREND_DOWN = -1



def init(PDI):
    global WeatherStations
    WeatherStations = dict()
    attrList = []    

    #read module configuration and initialize each device
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for wsCfg in cfgRoot.findall(WS_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                wsID = wsCfg.get('id')
                WeatherStations[wsID] = wsManager(PDI)
                WeatherStations[wsID].wsID = wsID
                
                #initialize outputs: get generically all outputs which are defined
                ioNameList = getClassAttributes(WeatherStations[wsID].outputs)      #['actTempIndoor', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = wsCfg.find('.//outputs/output[@name="' + ioName + '"]')
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
                            ioSignalInst = getattr(WeatherStations[wsID].outputs, ioName)              #get access to IO signal: "up", "down",...
                            ioSignalInst.addProcessTag(processTag.text, attrList)

                #initialize connection
                cfgItem = wsCfg.find('.//parameters/connection')
                #continue only if configuration exists
                if cfgItem != None:
                    WeatherStations[wsID].param.connection.url = cfgItem.attrib['url']

                #initialize weather station data
                wsDataItemCfg = wsCfg.find('.//parameters/wsdataitems')
                wsDataItemList = wsDataItemCfg.findall(WSDATAITEM_ELEMENT_NAME)
                for wsDataItem in wsDataItemList:
                    #add all data found to wsData dictionary
                    WeatherStations[wsID].param.wsData[wsDataItem.attrib['name']] = wsDataItem
                    WeatherStations[wsID].param.wsData[wsDataItem.attrib['name']].valueKey = wsDataItem.attrib['valuekey']
                    WeatherStations[wsID].param.wsData[wsDataItem.attrib['name']].valueType = wsDataItem.attrib['valuetype']
                    WeatherStations[wsID].param.wsData[wsDataItem.attrib['name']].mapping = wsDataItem.attrib['mapping']


                #initialize status points
                ioNameList = getClassAttributes(WeatherStations[wsID].status)      #['indoorSensorBattery', ...]
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="indoorSensorBattery">
                    statusCfg = wsCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(WeatherStations[wsID].status, ioName)              #get access to IO signal: "indoorSensorBattery", ...
                            ioSignalInst.addProcessTag(processTag.text, None)

                
            except Exception, e:
                print('Loading configuration for weather station <%s> failed: %s'%(e, wsID))
                return    

    except Exception, e:
        print('Loading weather station configuration failed: %s'%(e))
        return

def update(PDI):
    global WeatherStations

    for ws in WeatherStations:
        WeatherStations[ws].update(PDI)



class wsManager:
    #init
    def __init__(self, PDI):
        self.wsID = None
        self.PDI = PDI
        self.outputs = deviceOutputs(PDI)
        self.param = deviceParameters(PDI)
        self.status = deviceStatus(PDI)
        self.oldMinute = datetime.datetime.now().minute
        self.newMinuteRequestData = True        #request data immediately after power up
        self.requestThreadID = 0

        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sWS_DATA_REQUEST": self.sWS_DATA_REQUEST, 
                             "sWS_DATA_RESPONSE_WAIT": self.sWS_DATA_RESPONSE_WAIT, 
                             "sWS_DATA_RESPONSE_EXTRACT_DATA": self.sWS_DATA_RESPONSE_EXTRACT_DATA 
                            }
        self.activeState = "sIDLE"
        self.activeStateOld = ""
        self.httpRequestObj = 0
        self.httpResponseObj = 0
        self.httpResponseString = ""
        self.actTempOutdoorOld = 0
        self.relativePressureOld = 0
        self.uvRadiationIndexOld = 0
        self.actHumidityOutdoorOld = 0


    #cyclic logic    
    def update(self, PDI):
        if (self.oldMinute != datetime.datetime.now().minute):
            self.oldMinute = datetime.datetime.now().minute
            self.newMinuteRequestData = True

        #execute state machine
        self.statemachine[self.activeState]()
        #logging of state
        if (self.activeStateOld != self.activeState):
           self.activeStateOld = self.activeState
           print("Weather station <{0}> state: {1}".format(self.wsID, self.activeState))

    def requestDataThread(self):
        try:
            #prepare request
            self.httpRequestObj = urllib2.Request(self.param.connection.url, headers={ 'User-Agent': 'Mozilla/5.0' })
            # Sends the request and catches the response
            self.httpResponseObj = urllib2.urlopen(self.httpRequestObj)
            # Extracts the response
            self.httpResponseString = self.httpResponseObj.read()
            return
        except Exception, e:
            print("Weather station <{0}> http request failed: {1}".format(self.wsID, e))
            self.activeState = "sIDLE"
            return        


    def sIDLE(self):
        if (self.newMinuteRequestData == True):
            self.newMinuteRequestData = 0
            self.activeState = "sWS_DATA_REQUEST"
    

    def sWS_DATA_REQUEST(self):
        try:
            #start asynchronous thread to handle http request to not block cyclic system
            self.requestThreadID = threading.Thread(target=self.requestDataThread)
            self.requestThreadID.start()
            self.requestStartTime = time.time()
            self.activeState = "sWS_DATA_RESPONSE_WAIT"
            return
        except Exception, e:
            print("Weather station <{0}> thread start failed: {1}".format(self.wsID, e))
            self.activeState = "sIDLE"
            return        
        
        
    def sWS_DATA_RESPONSE_WAIT(self):
        if (self.requestThreadID.isAlive() == False):
            #print("Weather station <{0}>: http request successful".format(self.wsID))
            self.activeState = "sWS_DATA_RESPONSE_EXTRACT_DATA"
        elif ( (time.time() - self.requestStartTime) >= HTTP_REQUEST_TIMEOUT ):
            print("Weather station <{0}>: http request timeout".format(self.wsID))
            self.activeState = "sIDLE"
     
    def sWS_DATA_RESPONSE_EXTRACT_DATA(self):
        #print(self.httpResponseString)
        #extract weather station data from response string
        for wsDataName in self.param.wsData:
            #print(wsDataName)

            #httpResponseString contains the html response from the server
            itemPos = self.httpResponseString.find(wsDataName)
            valuePos = self.httpResponseString.find(self.param.wsData[wsDataName].valueKey, itemPos)
            
            try:
                #extract value with reg exp
                value = re.search('"(.+?)"', self.httpResponseString[valuePos:]).group(1)
                #print("Key {0}: {1}".format(wsDataName, value))
                
                #convert string if necessary
                if (self.param.wsData[wsDataName].valueType == VALUE_TYPE_REAL):
                    self.param.wsData[wsDataName].valueREAL = float(value)

                    try:
                        
                        #map value directly to PDI variable if mapping given
                        channel = getattr(self, self.param.wsData[wsDataName].mapping.split('.')[0])
                        ioSignal = getattr(channel, self.param.wsData[wsDataName].mapping.split('.')[1])
                        ioSignalValue = getattr(ioSignal, "value")
                        ioSignalValue(self.param.wsData[wsDataName].valueREAL)
                    except Exception, e:
                        print("Weather station <{0}>: error mapping value to PDI {1}".format(self.wsID, e))
                elif (self.param.wsData[wsDataName].valueType == VALUE_TYPE_TIME):
                    #convert weather station time stamp to Excel compatible timestamp: 22.01.2016  00:00:00 
                    self.param.wsData[wsDataName].valueTEXT = datetime.datetime.strptime(value, '%H:%M %m/%d/%Y').strftime("%d.%m.%Y %H:%M:%S")

                    try:
                        #map value directly to PDI variable if mapping given
                        channel = getattr(self, self.param.wsData[wsDataName].mapping.split('.')[0])
                        ioSignal = getattr(channel, self.param.wsData[wsDataName].mapping.split('.')[1])
                        ioSignalValue = getattr(ioSignal, "value")
                        ioSignalValue(self.param.wsData[wsDataName].valueTEXT)
                    except Exception, e:
                        print("Weather station <{0}>: error mapping value to PDI {1}".format(self.wsID, e))

                else:
                    self.param.wsData[wsDataName].valueTEXT = value

                    try:
                        #map value directly to PDI variable if mapping given
                        channel = getattr(self, self.param.wsData[wsDataName].mapping.split('.')[0])
                        ioSignal = getattr(channel, self.param.wsData[wsDataName].mapping.split('.')[1])
                        ioSignalValue = getattr(ioSignal, "value")
                        ioSignalValue(self.param.wsData[wsDataName].valueTEXT)
                    except Exception, e:
                        print("Weather station <{0}>: error mapping value to PDI {1}".format(self.wsID, e))
                    
            except Exception, e:
                print("Weather station <{0}>: error parsing http response {1}".format(self.wsID, e))

        
        #calculate additional values from live data
        #general weather condition
        if (self.outputs.uvRadiation.value() >= 1000):
            self.outputs.weatherCondition.value(WEATHER_CONDITION_SUNNY)
        elif (self.outputs.uvRadiation.value() >= 500):
            self.outputs.weatherCondition.value(WEATHER_CONDITION_PARTLY_SUNNY)
        else:
            self.outputs.weatherCondition.value(WEATHER_CONDITION_CLOUDED)
            if (self.outputs.rainHourly.value() > 0):
                if (self.outputs.actTempOutdoor.value() > -2.0):
                    self.outputs.weatherCondition.value(WEATHER_CONDITION_RAIN)
                else:
                    self.outputs.weatherCondition.value(WEATHER_CONDITION_SNOW)
        
        #generate cloudy signal for weather stations (auto shading)
        if (self.outputs.weatherCondition.value() != WEATHER_CONDITION_SUNNY) and (self.outputs.weatherCondition.value() != WEATHER_CONDITION_PARTLY_SUNNY):
            self.outputs.isCloudy.value(1)
        else:
            self.outputs.isCloudy.value(0)
            
        #calculate feels like temperature
        if (self.outputs.actTempOutdoor.value() <= 10.0) and (self.outputs.windSpeed.value() >= 5.0):
            #apparent temperature (feels like) is influenced by wind chill: https://de.wikipedia.org/wiki/Windchill
            self.outputs.actTempOutdoorFeelsLike.value( 13.12 + \
                                                        0.6215 * self.outputs.actTempOutdoor.value() - \
                                                        11.37 * math.pow(self.outputs.windSpeed.value(), 0.16) + \
                                                        0.3965 * self.outputs.actTempOutdoor.value() * math.pow(self.outputs.windSpeed.value(), 0.16) )
            
        elif ((self.outputs.actTempOutdoor.value() >= 26.7) and (self.outputs.actHumidityOutdoor.value() >= 40.0)):
            #apparent temperature (feels like) is influenced by heat index: https://de.wikipedia.org/wiki/Hitzeindex
            self.outputs.actTempOutdoorFeelsLike.value( -8.784695 + \
                                                        1.61139411  * self.outputs.actTempOutdoor.value()     + \
                                                        2.338549    * self.outputs.actHumidityOutdoor.value() + \
                                                        -0.14611605 * self.outputs.actTempOutdoor.value()     * self.outputs.actHumidityOutdoor.value()              + \
                                                        -1.2308094  * math.expm1(1e-2)                        * math.pow(self.outputs.actTempOutdoor.value(), 2)     + \
                                                        -1.6424828  * math.expm1(1e-2)                        * math.pow(self.outputs.actHumidityOutdoor.value(), 2) + \
                                                        2.211732    * math.expm1(1e-3)                        * math.pow(self.outputs.actTempOutdoor.value(), 2)     * self.outputs.actHumidityOutdoor.value() + \
                                                        7.2546      * math.expm1(1e-4)                        * self.outputs.actTempOutdoor.value()                  * math.pow(self.outputs.actHumidityOutdoor.value(), 2) + \
                                                        -3.582      * math.expm1(1e-6)                        * math.pow(self.outputs.actTempOutdoor.value(), 2)     * math.pow(self.outputs.actHumidityOutdoor.value(), 2) )
        else:
            self.outputs.actTempOutdoorFeelsLike.value(self.outputs.actTempOutdoor.value())


        #calculate outdoor temperature trend
        if (abs(self.outputs.actTempOutdoor.value() - self.actTempOutdoorOld) >= THRESHOLD_ACT_TEMP_TREND):
            if (self.outputs.actTempOutdoor.value() > self.actTempOutdoorOld):
                self.outputs.actTempOutdoorTrend.value(TREND_UP)
            else:
                self.outputs.actTempOutdoorTrend.value(TREND_DOWN)

            self.actTempOutdoorOld = self.outputs.actTempOutdoor.value()
        else:
            self.outputs.actTempOutdoorTrend.value(TREND_NO_CHANGE)
        
        #calculate relative pressure trend
        if (abs(self.outputs.relativePressure.value() - self.relativePressureOld) >= THRESHOLD_REL_PRESSURE_TREND):
            if (self.outputs.relativePressure.value() > self.relativePressureOld):
                self.outputs.relativePressureTrend.value(TREND_UP)
            else:
                self.outputs.relativePressureTrend.value(TREND_DOWN)

            self.relativePressureOld = self.outputs.relativePressure.value()
        else:
            self.outputs.relativePressureTrend.value(TREND_NO_CHANGE)

        #calculate UV radiation trend
        if (abs(self.outputs.uvRadiationIndex.value() - self.uvRadiationIndexOld) >= THRESHOLD_UV_INDEX_TREND):
            if (self.outputs.uvRadiationIndex.value() > self.uvRadiationIndexOld):
                self.outputs.uvRadiationIndexTrend.value(TREND_UP)
            else:
                self.outputs.uvRadiationIndexTrend.value(TREND_DOWN)

            self.uvRadiationIndexOld = self.outputs.uvRadiationIndex.value()
        else:
            self.outputs.uvRadiationIndexTrend.value(TREND_NO_CHANGE)

       #calculate outdoor humidity trend
        if (abs(self.outputs.actHumidityOutdoor.value() - self.actHumidityOutdoorOld) >= THRESHOLD_HUMIDITY_TREND):
            if (self.outputs.actHumidityOutdoor.value() > self.uvRadiationIndexOld):
                self.outputs.actHumidityOutdoorTrend.value(TREND_UP)
            else:
                self.outputs.actHumidityOutdoorTrend.value(TREND_DOWN)

            self.actHumidityOutdoorOld = self.outputs.actHumidityOutdoor.value()
        else:
            self.outputs.actHumidityOutdoorTrend.value(TREND_NO_CHANGE)

        self.activeState = "sIDLE"




class deviceOutputs():
    'Collection of outputs of a certain weather station'
    #init
    def __init__(self, PDI):
        self.recordTimeStamp = core.modules.iosignal.IOsignal(PDI)
        self.actTempIndoor = core.modules.iosignal.IOsignal(PDI)
        self.actTempOutdoor = core.modules.iosignal.IOsignal(PDI)
        self.actTempOutdoorFeelsLike = core.modules.iosignal.IOsignal(PDI)
        self.actHumidityIndoor = core.modules.iosignal.IOsignal(PDI)
        self.actHumidityOutdoor = core.modules.iosignal.IOsignal(PDI)
        self.absolutePressure = core.modules.iosignal.IOsignal(PDI)
        self.relativePressure = core.modules.iosignal.IOsignal(PDI)
        self.windDirection = core.modules.iosignal.IOsignal(PDI)
        self.windSpeed = core.modules.iosignal.IOsignal(PDI)
        self.windGust = core.modules.iosignal.IOsignal(PDI)
        self.solarRadiation = core.modules.iosignal.IOsignal(PDI)
        self.uvRadiation = core.modules.iosignal.IOsignal(PDI)
        self.uvRadiationIndex = core.modules.iosignal.IOsignal(PDI)
        self.rainHourly = core.modules.iosignal.IOsignal(PDI)
        self.weatherCondition = core.modules.iosignal.IOsignal(PDI)
        self.isCloudy = core.modules.iosignal.IOsignal(PDI)
        self.actTempOutdoorTrend = core.modules.iosignal.IOsignal(PDI)
        self.relativePressureTrend = core.modules.iosignal.IOsignal(PDI)
        self.uvRadiationIndexTrend = core.modules.iosignal.IOsignal(PDI)
        self.actHumidityOutdoorTrend = core.modules.iosignal.IOsignal(PDI)

class deviceParameters():
    #init
    def __init__(self, PDI):
        self.connection = paramConnection()
        self.wsData = dict()        #dictionary of wsDataItem

class paramConnection():
    #init
    def __init__(self):
        self.url = ""           #URL to weather station
        
class wsDataItem():
    #init
    def __init__(self):
        self.valueREAL = 0.0
        self.valueTEXT= ""
        self.valueKey = None
        self.valueType = None
        self.mapping = None


class deviceStatus:
    #init
    def __init__(self, PDI):
        self.indoorSensorBattery = core.modules.iosignal.IOsignal(PDI);
        self.outdoorSensorBattery = core.modules.iosignal.IOsignal(PDI);




#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    



''' DEBUGGING '''
if __name__ == "__main__":
    init(None)
               