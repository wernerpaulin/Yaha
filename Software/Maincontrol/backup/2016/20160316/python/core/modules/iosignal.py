#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

INITIAL_STATE_NORMALLY_OPEN = "normallyOpen"
INITIAL_STATE_NORMALLY_CLOSED = "normallyClosed"
LOGIC_OR = "or"
LOGIC_AND = "and"

class IOsignal:
    'IO data point to PDI'

    #init
    def __init__(self, PDI):
        self.processTags = dict()
        self.PDI = PDI

    def addProcessTag(self, tagName, attributeList):
       self.processTags[tagName] = attributeList    #["normallyOpen", "and",...]
       
    def value(self, signalValue=None):
        #read: if no value is given it is assumed that the current IO value has to be evaluated and returned
        if signalValue == None:
            signalValue = 0
            
            #calculate signal value out of linked PDI process tags
            for tag in self.processTags:
                #get value of process tag
                pdiValue = getattr(self.PDI, tag)
                tagAttributeList = self.processTags[tag]
                
                if tagAttributeList != None:
                    #evaluate attribute for input signal
                    if INITIAL_STATE_NORMALLY_OPEN in tagAttributeList:      #active = 1
                        if pdiValue > 0:
                            pdiValue = 1
                        else:
                            pdiValue = 0
                            
                    elif INITIAL_STATE_NORMALLY_CLOSED in tagAttributeList:  #active = 0
                        if pdiValue > 0:
                            pdiValue = 0
                        else:
                            pdiValue = 1
                    else:
                        pass    #no manipulation in case no such attribute is given: analog value
    
                    #evaluate attribute for logical link of PDI values to form signal                
                    if LOGIC_AND in tagAttributeList: 
                        signalValue = signalValue and pdiValue
                    elif LOGIC_OR in tagAttributeList:
                        signalValue = signalValue or pdiValue
                    else:
                        signalValue = pdiValue  #for all analog values
                        
                else:
                    signalValue = pdiValue  #no attributes given
                    
            #return calculated signal
            return signalValue   
                
        #write: if a value is given then this value will be written to all assigned processTags
        else:
            #write signal value to linked PDI process tags
            for tag in self.processTags:
                #evaluate attribute for output signal
                tagAttributeList = self.processTags[tag]
                
                if tagAttributeList != None:
                    if INITIAL_STATE_NORMALLY_OPEN in tagAttributeList:      #active = 1
                        if signalValue > 0:
                            setattr(self.PDI, tag, 1)
                        else:
                            setattr(self.PDI, tag, 0)
                            
                    elif INITIAL_STATE_NORMALLY_CLOSED in tagAttributeList:  #active = 0
                        if signalValue > 0:
                            setattr(self.PDI, tag, 0)
                        else:
                            setattr(self.PDI, tag, 1)
                    else:
                        setattr(self.PDI, tag, signalValue)    #no manipulation in case no such attribute is given: analog value
                else:
                    setattr(self.PDI, tag, signalValue)    #no manipulation in case no such attribute is given: analog value
                    
