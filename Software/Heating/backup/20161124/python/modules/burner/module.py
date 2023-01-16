#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time


def init(PDI):
    pass



def update(PDI):
    if (PDI.burnerManOp == 1):
        PDI.burnerTotalOperatingHours = 5000
        PDI.burnerState = 1
    else:
        PDI.burnerTotalOperatingHours = 2000
        PDI.burnerState = 0
    
    #print(PDI.burnerState)
        
    if (PDI.burnerManControllerRelease == 1):
        PDI.burnerAnnualOperatingHours = 5000
    else:
        PDI.burnerAnnualOperatingHours = 2000
        
    #print(PDI.burnerManSetTemp)
