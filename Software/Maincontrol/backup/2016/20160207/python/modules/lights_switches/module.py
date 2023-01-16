#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py
#python /home/pi/Yaha/modules/lights_switches/module.py



MODULE_CFG_FILE_NAME = "module.cfg.xml"
SWITCH_CFG_ELEMENT_NAME = "./switches/switch"
PROCESSTAG_ELEMENT_NAME = "processtag"
OUTPUTMODE_ELEMENT_NAME = "outputmode"
OUTPUTMODE_IMPULSE_NAME = "impulse"
OUTPUTMODE_OFFDELAY_NAME = "offdelay"

import os
import xml.etree.ElementTree as xmlParser
import core.modules.iosignal
import datetime, time
import calendar

def init(PDI):
    global Switches
    Switches = dict()
    ioList = []
    attrList = []

    #read module configuration and initialize each device
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for switchCfg in cfgRoot.findall(SWITCH_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                switchID = switchCfg.get('id')
                Switches[switchID] = switchManager(PDI)
                
                #initialize inputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Switches[switchID].inputs)      #['brightness', 'color', 'off', 'on', 'teach']
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <input name="on">
                    inputCfg = switchCfg.find('.//inputs/input[@name="' + ioName + '"]')
                    #get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
                    processTagList = inputCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                    #add processTags to IO signal
                    for processTag in processTagList:
                        #convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
                        attrList = []
                        for attr in processTag.attrib:
                            attrList.append(processTag.attrib[attr])
    
                        #each IOsignal has an addProcessTag function: call it generically depending on ioName
                        ioSignalInst = getattr(Switches[switchID].inputs, ioName)              #get access to IO signal: "on", "off",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)
                
                
                #initialize outputs: get generically all inputs which are defined
                ioNameList = getClassAttributes(Switches[switchID].outputs)      #['brightness', 'color', 'off', 'on', 'teach']
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    outputCfg = switchCfg.find('.//outputs/output[@name="' + ioName + '"]')
                    #get all mapped PDI process tags: <processtag initialstate="normallyOpen">xxx</processtag>
                    processTagList = outputCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                    #add processTags to IO signal
                    for processTag in processTagList:
                        #convert all attributes which are given as dictionary from xml parser to list with only their values: ["normallyOpen", "and",...]
                        attrList = []
                        for attr in processTag.attrib:
                            attrList.append(processTag.attrib[attr])
    
                        #each IOsignal has an addProcessTag function: call it generically depending on ioName
                        ioSignalInst = getattr(Switches[switchID].outputs, ioName)              #get access to IO signal: "on", "off",...
                        ioSignalInst.addProcessTag(processTag.text, attrList)

    
                #initialize blink logic
                ioNameList = getClassAttributes(Switches[switchID].param.blink)      #['enable', 'offIntervall', 'onIntervall']
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <output name="on">
                    logicCfg = switchCfg.find('.//logic/blink/' + ioName)
                    #continue only if configuration exists
                    if logicCfg != None:
                        #get mapped PDI process tag: <processtag>light1BlinkEnable</processtag>
                        processTag = logicCfg.find(PROCESSTAG_ELEMENT_NAME)                 
                        #each IOsignal has an addProcessTag function: call it generically depending on ioName
                        ioSignalInst = getattr(Switches[switchID].param.blink, ioName)              #get access to IO signal: "on", "off",...
                        ioSignalInst.addProcessTag(processTag.text, None)

    
                #initialize status points
                ioNameList = getClassAttributes(Switches[switchID].status)      #['ontime', 'energy', 'switchlevel']
                #try to find the corresponding PDI mapping in the configuration file 
                for ioName in ioNameList:
                    #get access to input configuration: <statusitem name="ontime">
                    statusCfg = switchCfg.find('.//statusitems/statusitem[@name="' + ioName + '"]')
                    #continue only if configuration exists
                    if statusCfg != None:
                        #get all mapped PDI process tags: <processtag>xxx</processtag>
                        processTagList = statusCfg.findall(PROCESSTAG_ELEMENT_NAME) 
                        #add processTags to IO signal
                        for processTag in processTagList:
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Switches[switchID].status, ioName)              #get access to IO signal: "ontime", "energy",...
                            ioSignalInst.addProcessTag(processTag.text, None)

    
                #initialize output mode: get generically all output modes which are defined
                outputModeCfg = switchCfg.find('.//logic/outputmodes')
                if outputModeCfg != None:
                    #get access to outputmode configuration: <outputmode type="impulse">
                    outputModeList = outputModeCfg.findall(OUTPUTMODE_ELEMENT_NAME)
                    for outputmode in outputModeList:
                        #set up instance for each output mode: outputmode.attrib['type']: impulse,...
                        Switches[switchID].param.outputmode[outputmode.attrib['type']] = paramOutputmode(PDI)
        
                        #try to find the corresponding PDI mapping in the configuration file for each class attribute
                        ioNameList = getClassAttributes(Switches[switchID].param.outputmode[outputmode.attrib['type']])      #['enable', 'duration']
                        for ioName in ioNameList:
                            logicCfg = outputmode.find(ioName)
                            #get mapped PDI process tag: <processtag>light1BlinkEnable</processtag>
                            processTag = logicCfg.find(PROCESSTAG_ELEMENT_NAME)                 
                            #each IOsignal has an addProcessTag function: call it generically depending on ioName
                            ioSignalInst = getattr(Switches[switchID].param.outputmode[outputmode.attrib['type']], ioName)              #get access to IO signal: "on", "off",...
                            ioSignalInst.addProcessTag(processTag.text, None)
     
                "TODO: time auslesen"
                print(datetime.datetime.now().timetuple().tm_yday) #day of year
                
                
            except Exception, e:
                print('Loading configuration for switch <%s> failed: %s'%(e, switchID))
                return    

    except Exception, e:
        print('Loading light & switches module configuration failed: %s'%(e))
        return

    

def update(PDI):
    global Switches

    for switch in Switches:
        Switches[switch].update(PDI)



class switchManager:
    #init
    def __init__(self, PDI):
        self.inputs = deviceInputs(PDI)
        self.outputs = deviceOutputs(PDI)
        self.param = deviceParameters(PDI)
        self.status = deviceStatus(PDI)
        self.blinkStartTime = 0
        self.impulseStartTime = 0
        self.offDelayStartTime = 0

        self.statemachine = {
                             "sIDLE": self.sIDLE,
                             "sSWITCH_ON": self.sSWITCH_ON,
                             "sSWITCH_OFF": self.sSWITCH_OFF,
                             "sIMPULSE": self.sIMPULSE,
                             "sSWITCH_OFF_DELAY":self.sSWITCH_OFF_DELAY,
                             "sBLINK_INIT": self.sBLINK_INIT,
                             "sBLINK_ON": self.sBLINK_ON,
                             "sBLINK_OFF": self.sBLINK_OFF,
                             "sTIME_BASE": self.sTIME_BASE,
                             "sTIME_ON": self.sTIME_ON,
                             "sTIME_OFF": self.sTIME_OFF,
                             "sTEACH_START": self.sTEACH_START,
                             "sTEACH_END": self.sTEACH_END
                            }
        self.activeState = "sIDLE"

    
    #cyclic logic    
    def update(self, PDI):
        #execute state machine
        self.statemachine[self.activeState]()
 
    def sIDLE(self):
        #check for switch off (has overall priority)
        if self.inputs.off.value() == 1:
            self.inputs.off.value(0)
            self.activeState = "sSWITCH_OFF"
            
        elif self.inputs.on.value() == 1:
            self.inputs.on.value(0)
            self.activeState = "sSWITCH_ON"
        
        elif self.inputs.teach.value() == 1:
            self.inputs.teach.value(0)
            self.activeState = "sTEACH_START"

        elif self.param.blink.enable.value() == 1:
            self.activeState = "sBLINK_INIT"


    def sSWITCH_ON(self):
        self.outputs.on.value(1)

        #check whether an impulse is configured and enabled
        try:
            if (self.param.outputmode[OUTPUTMODE_IMPULSE_NAME].enable.value() == 1):
                self.activeState = "sIMPULSE"
                self.impulseStartTime = time.time()
            else:
                self.activeState = "sIDLE"
        except:
            self.activeState = "sIDLE"
        return

    def sSWITCH_OFF(self):
        #check whether an off delay is configured and enabled
        try:
            if (self.param.outputmode[OUTPUTMODE_OFFDELAY_NAME].enable.value() == 1):
                self.activeState = "sSWITCH_OFF_DELAY"
                self.offDelayStartTime = time.time()
            else:
                self.outputs.off.value(1)
                self.activeState = "sIDLE"
        except:
            self.outputs.off.value(1)
            self.activeState = "sIDLE"
        return

    def sIMPULSE(self):
        #stop impulse if requested
        if (self.param.outputmode[OUTPUTMODE_IMPULSE_NAME].enable.value() == 0) or (self.inputs.off.value() == 1):
          self.param.outputmode[OUTPUTMODE_IMPULSE_NAME].enable.value(0)
          self.inputs.off.value(0)
          self.activeState = "sSWITCH_OFF"
          return
        
        if (time.time() >= self.impulseStartTime + self.param.outputmode[OUTPUTMODE_IMPULSE_NAME].duration.value()):
            self.activeState = "sSWITCH_OFF"
            return        

    def sSWITCH_OFF_DELAY(self):
        #wait until time is elapsed, then switch off
        if (time.time() >= self.offDelayStartTime + self.param.outputmode[OUTPUTMODE_OFFDELAY_NAME].duration.value()):
            self.outputs.off.value(1)
            self.activeState = "sIDLE"
        return

    def sBLINK_INIT(self):
        self.blinkStartTime = time.time()
        self.activeState = "sBLINK_ON"
        return
 

    def sBLINK_ON(self):
        #stop blink sequence if requested
        if (self.param.blink.enable.value() == 0) or (self.inputs.off.value() == 1):
          self.param.blink.enable.value(0)
          self.inputs.off.value(0)
          self.activeState = "sSWITCH_OFF"
          return
        
        if (time.time() >= self.blinkStartTime + self.param.blink.onintervall.value()):
            self.outputs.on.value(1)
            self.blinkStartTime = time.time()
            self.activeState = "sBLINK_OFF"
            return


    def sBLINK_OFF(self):
        #stop blink sequence if requested
        if (self.param.blink.enable.value() == 0) or (self.inputs.off.value() == 1):
          self.param.blink.enable.value(0)
          self.inputs.off.value(0)
          self.activeState = "sSWITCH_OFF"
          return
        
        if (time.time() >= self.blinkStartTime + self.param.blink.offintervall.value()):
            self.outputs.off.value(1)
            self.blinkStartTime = time.time()
            self.activeState = "sBLINK_ON"
            return

    def sTIME_BASE(self):
        pass

    def sTIME_ON(self):
        pass

    def sTIME_OFF(self):
        pass

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
        self.on = core.modules.iosignal.IOsignal(PDI)
        self.off = core.modules.iosignal.IOsignal(PDI)
        self.brightness = core.modules.iosignal.IOsignal(PDI)
        self.color = core.modules.iosignal.IOsignal(PDI)
        self.teach = core.modules.iosignal.IOsignal(PDI)

class deviceOutputs():
    'Collection of outputs of a certain device'
    
    #init
    def __init__(self, PDI):
        self.on = core.modules.iosignal.IOsignal(PDI)
        self.off = core.modules.iosignal.IOsignal(PDI)
        self.brightness = core.modules.iosignal.IOsignal(PDI)
        self.color = core.modules.iosignal.IOsignal(PDI)
        self.teach = core.modules.iosignal.IOsignal(PDI)

class paramBlink():
    #init
    def __init__(self, PDI):
        self.enable = core.modules.iosignal.IOsignal(PDI)
        self.onintervall = core.modules.iosignal.IOsignal(PDI)
        self.offintervall = core.modules.iosignal.IOsignal(PDI)

class paramOutputmode():
    #init
    def __init__(self, PDI):
        self.enable = core.modules.iosignal.IOsignal(PDI)
        self.duration = core.modules.iosignal.IOsignal(PDI)

class deviceParameters:
    #init
    def __init__(self, PDI):
        self.blink = paramBlink(PDI)
        self.outputmode = dict()    #paramOutputmode

class deviceStatus:
    #init
    def __init__(self, PDI):
        self.ontime = core.modules.iosignal.IOsignal(PDI);
        self.energy = core.modules.iosignal.IOsignal(PDI);
        self.switchlevel = core.modules.iosignal.IOsignal(PDI);

        



#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
    

''' DEBUGGING '''
if __name__ == "__main__":
    init(None)
                
