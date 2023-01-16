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