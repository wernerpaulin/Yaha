#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import math

class PID:
    'discrete PID closed loop control'
    #init
    def __init__(self):
        self.e = 0                #control deviation e = w-x
        self.Kp = 0               #proportional gain
        self.Ti = 0               #integral action time
        self.i_max = 0            #maximum integral action
        self.Td = 0               #derivative action time
        self.T1 = 0               #filter time
        self.Ta = 0               #sample time of PID controller
        self.y_max = 0            #maximum output limitation
        self.y_min = 0            #minimum output limitation
        self.y = 0                #output signal
        self.yp = 0               #proportional part
        self.yi = 0               #integral part
        self.yd = 0               #differencial part
        self.ydt1 = 0             #filtered d-part by T1
        self.yp_old = 0           #last yp used for d-part (internal use only)
        self.i_lim = 0            #actual anit wind-up limitation (internal use only)
        self.yiHold = 0           #1 ...holds yi part at actual value
        
        self.lastCallTimestamp = time.time()    #used to calculate sampling time

    
    def update(self):
        self.Ta = time.time() - self.lastCallTimestamp
        self.lastCallTimestamp = time.time()        

        #P part
        self.yp = self.e * self.Kp                                                                      
        
        #I part with anti wind-up limitation
        if (self.Ti > 0):
            #anti wind-up limitation
            self.i_lim = max(self.i_max - abs(self.yp), 0)                                              
            
            if (self.yiHold == False):
                self.yi = max(min(self.yi + (self.yp * self.Ta / self.Ti), self.i_lim), -self.i_lim)    
        else:
            self.yi = 0
    
        #D part
        if (self.Ta > 0):
            self.yd = self.Kp * self.Td/self.Ta * (self.yp - self.yp_old)
            self.yp_old = self.yp

            #filter yd by T1
            if (self.T1 > 0):
                self.ydt1 = (1 - self.Ta/self.T1) * self.ydt1 + (self.Ta/self.T1) * self.yd
            else:
                self.ydt1 = self.yd
        
        else:
            self.yd = 0
            self.yp_old = 0
            self.ydt1 = 0
    
        
        #sum up all PID parts
        self.y = self.yp + self.yi + self.ydt1
        self.y = max(min(self.y, self.y_max), self.y_min)
        
        return