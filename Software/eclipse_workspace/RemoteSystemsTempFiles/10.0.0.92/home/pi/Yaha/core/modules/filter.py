#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import math

class PT1:
    'discrete filtering of PT1'

    #init
    def __init__(self):
        self.lastCallTimestamp = time.time()    #used to calculate sampling time
        self.lastOutputValue = 0                #last / current value
        self.samplingTime = 0                   #sampling time
        
    def update(self, targetValue, tau, gain):   #target value reached with tau as time constant of path, gain of path
        self.samplingTime = time.time() - self.lastCallTimestamp
        self.lastCallTimestamp = time.time()

        try:
            self.lastOutputValue = math.exp(-self.samplingTime/tau) * self.lastOutputValue + gain * targetValue * (1 - math.exp(-self.samplingTime/tau))
        except Exception as e:
            print("PT1 filter calculation error: <{0}>".format(e))
            self.lastOutputValue = 0
        
        return (self.lastOutputValue)
    
    
class PT2:
    'discrete filtering of PT2 (2x PT1)'

    #init
    def __init__(self):
        self.PT1_1 = PT1()
        self.PT1_2 = PT1()
        self.outputPT1_1 = 0
        self.outputPT1_2 = 0

    def update(self, targetValue, tau, gain):   #target value reached with tau as time constant of path, gain of path
        self.outputPT1_1 = self.PT1_1.update(targetValue, tau, gain)
        self.outputPT1_2 = self.PT1_1.update(self.outputPT1_1, tau, gain)
        
        return (self.outputPT1_2)

        