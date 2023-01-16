#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import core.dt_handler.yaha_datetime

def init(PDI):
    global dateTimeManager
    dateTimeManager = core.dt_handler.yaha_datetime.Manager()
    
def update(PDI):
    ''' DATE and TIME handling '''
    PDI.cmdSetDateTime = dateTimeManager.setDateTimeHandler(PDI.cmdSetDateTime, PDI.setDateString, PDI.setTimeString)
    PDI.currentYear, PDI.currentMonth, PDI.currentDay = dateTimeManager.getDate()
    PDI.currentHour, PDI.currentMinute, PDI.currentSecond = dateTimeManager.getTime()
