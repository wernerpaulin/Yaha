#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py


import os
import xml.etree.ElementTree as xmlParser
import datetime, time

import core.modules.iosignal

MODULE_CFG_FILE_NAME = "module.cfg.xml"
PROCESSTAG_ELEMENT_NAME = "processtag"

IO_SIMULATION_ACTIVE_PDI_TAG = "ioSimulation"

def init(PDI):
	pass

def update(PDI):
	pass

    
        
#get all properties of a class: dir() returns also dynamically added ones but also internal methods (filtered with __)
def getClassAttributes(c):
    return [p for p in dir(c) if not callable(getattr(c,p)) and not p.startswith("__")]
        