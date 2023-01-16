#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time


def init(PDI):
    pass



def update(PDI):
    PDI.floorHeatingMixerActPosition = PDI.floorHeatingMixerActPosition + 1
    if (PDI.floorHeatingMixerActPosition >= 99):
        PDI.floorHeatingMixerActPosition = 0
        
    if (PDI.floorHeatingMixerActPosition < 50):
        PDI.floorHeatingMixerState = 0
    else:
        PDI.floorHeatingMixerState = 1
        
    #print(PDI.floorHeatingMixerManSetPosition)
    #print(PDI.floorHeatingMixerManHoming)
    #if (PDI.floorHeatingMixerManHoming == 1):
    #    if (PDI.floorHeatingControllerState == 1):
    #       PDI.floorHeatingControllerState = 0
    #    else:
    #       PDI.floorHeatingControllerState = 1

    #    PDI.floorHeatingMixerManHoming = 0
        
    #PDI.floorHeatingSetFlowTemp = 33
    
    #PDI.actTempFlowRadiator = PDI.actTempFlowRadiator + 10.3333333
    #if (PDI.actTempFlowRadiator >= 99):
    #    PDI.actTempFlowRadiator = -80   
    