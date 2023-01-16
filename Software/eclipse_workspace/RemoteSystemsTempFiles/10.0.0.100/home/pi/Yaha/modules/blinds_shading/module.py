#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py


MODULE_CFG_FILE_NAME = "module.cfg.xml"
SWITCH_CFG_ELEMENT_NAME = "./blinds/blind"
PROCESSTAG_ELEMENT_NAME = "processtag"
OUTPUTMODE_ELEMENT_NAME = "outputmode"
ENABLE_ELEMENT_NAME = "enable"
EVENT_ELEMENT_NAME = "event"
DATERANGES_ELEMENT_NAME = "dateranges"
DATERANGE_ELEMENT_NAME = "daterange"
START_ELEMENT_NAME = "start"
END_ELEMENT_NAME = "end"
WEEKDAYS_ELEMENT_NAME = "weekdays"
WEEKDAY_ELEMENT_NAME = "weekday"
EVENT_ACTION_UP = "up"
EVENT_ACTION_DOWN = "down"


import os
import xml.etree.ElementTree as xmlParser
import datetime, time

import core.modules.iosignal
from core.modules.cal_event import *


def init(PDI):
    global Blinds
    Blinds = dict()
    ioList = []
    attrList = []    

def update(PDI):
    pass
  

'''WEITER MACHEN:
1. Klassen definieren
2. init Funktion

'''
