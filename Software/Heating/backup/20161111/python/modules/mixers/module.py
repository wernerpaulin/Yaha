#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time


def init(PDI):
    pass



def update(PDI):
    #print(PDI.floorHeatingMixerManSetPosition)
    #print(PDI.floorHeatingMixerManHoming)
    if (PDI.floorHeatingMixerManHoming == 1):
        if (PDI.floorHeatingControllerState == 1):
           PDI.floorHeatingControllerState = 0
        else:
           PDI.floorHeatingControllerState = 1

        PDI.floorHeatingMixerManHoming = 0
        
    PDI.floorHeatingSetFlowTemp = 33