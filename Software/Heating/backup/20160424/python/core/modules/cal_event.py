#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import datetime, time

class calEvent:
    "Calender driven event definition"
    #init
    def __init__(self):
        self.action = None
        self.dateRangeList = [] #eventDateRange
        self.triggerHour = None
        self.triggerMinute = None

    #evaluate base on date, week day and time whether an action should be initiated    
    def getAction(self, calDate):
        calDateDayIndex = calDate.timetuple().tm_yday
        calDateWeekDayIndex = calDate.timetuple().tm_wday
        calDateHour = calDate.hour
        calDateMinute = calDate.minute

        #loop through all given ranges (start - end) and cross check with week day restriction whether the event should be put into the calender
        for dateRange in self.dateRangeList:
            if (calDateDayIndex >= dateRange.startDayIndex) and (calDateDayIndex <= dateRange.endDayIndex):
                #calendar date (current day) is in range if this event -> check whether there is a week day limitation
                if (calDateWeekDayIndex in dateRange.weekDayList):
                    #check whether time has been reached
                    if (calDateHour == self.triggerHour) and (calDateMinute == self.triggerMinute):
                        return self.action
                    else:
                        return None
                else:
                    return None
            else:
                return None        
        return None

class calEventDateRange:
    #init
    def __init__(self):
        self.startDayIndex = None    
        self.endDayIndex = None
        self.hour = None
        self.minute = None    
        self.weekDayList = []   #0-6
