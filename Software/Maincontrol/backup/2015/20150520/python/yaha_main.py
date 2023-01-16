#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import datetime, threading, time
import yaha_pdi

SYSTEM_TICK_CYCLE_TIME = 0.2    #seconds
YAHA_PDI_DEFINITION_FILE = 'C:/Users/paulinw/Desktop/Home Automation/Yaha/backup/trunk/python/pdi/yaha_pdi.xml'
#YAHA_PDI_DEFINITION_FILE = '/home/pi/Yaha/yaha_pdi.xml'


PDI = yaha_pdi.clYaha_pdi(YAHA_PDI_DEFINITION_FILE)

def SystemInit():
    print("SystemInit()")

def SystemTick(cycleTime):
    cycleTime = max(cycleTime, 0.01)    #limit to 10ms - just in case given value is 0 or too small
    nextStartTime = time.time()

    while True:
        PDI.read()

        #################### BEGIN OF CYCLIC CODE #################### 
        #print(PDI.count1)
        PDI.count1 = PDI.count1 + 1
        PDI.var1 = PDI.var1 + 1
        PDI.var2 = PDI.var2 + 1
        PDI.var3 = PDI.var3 + 1

 
        ##################### END OF CYCLIC CODE ##################### 

        #write process data and prepare next cycle
        PDI.write()

        nextStartTime = nextStartTime + cycleTime
        PDI.systemTickRunTime = nextStartTime - time.time()
        PDI.cpuLoad = 1.0 - (PDI.systemTickRunTime / cycleTime)
        try:
            time.sleep(nextStartTime - time.time()) #sleep time by runtime of previous cycle
        except ValueError:                          #cycle time violation: skip compensation 
            print('Cycle time violation: %s'%(nextStartTime - time.time()))
            time.sleep(cycleTime)  


#initialize system
SystemInit()

#start cyclic system
timerThread = threading.Thread(target=SystemTick(SYSTEM_TICK_CYCLE_TIME))
timerThread.start()






# compensate time() call, adjust sleep according to runtime of function, watchdog
"""
#Zugriff auf Process Data Image
import threading

L = threading.Lock()

L.acquire()
# The critical section ...
L.release()
"""
