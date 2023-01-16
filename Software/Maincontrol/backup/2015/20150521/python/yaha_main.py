#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import datetime, time
import threading
import yaha_data
import yaha_ui
import yaha_enocean


SYSTEM_TICK_CYCLE_TIME = 0.2    #seconds
#YAHA_PDI_DEFINITION_FILE = 'C:/Users/paulinw/Desktop/Home Automation/Yaha/backup/trunk/python/pdi/yaha_pdi.xml'
YAHA_PDI_DEFINITION_FILE = '/home/pi/Yaha/pdi/yaha_pdi.xml'


def SystemTick():
    #initialize system tick    
    nextStartTime = time.time()
    PDI = yaha_data.ProcessDataImage(YAHA_PDI_DEFINITION_FILE)
    uiServer = yaha_ui.Server()
    enoceanDriver = yaha_enocean.Driver()

    while True:
        enoceanDriver.update()
        uiServer.update()
        PDI.read()

        #################### BEGIN OF CYCLIC CODE #################### 
        PDI.count1 = PDI.count1 + 1
        PDI.var1 = PDI.var1 + 1
        PDI.var2 = PDI.var2 + 1
        PDI.var3 = PDI.var3 + 1

        PDI.selectText = PDI.selectGroup #selectStandard
        PDI.selectText = PDI.selectGroup #selectStandard

        PDI.logEnocean = enoceanDriver.logEnocean

        #if (PDI.checkboxgroup2 == 'true'):
        #    PDI.checkboxgroup2 = 'false'
     
        #PDI.radiogroup1
        #PDI.checkboxgroup2
        #PDI.radiogroup2
     
     
        ##################### END OF CYCLIC CODE ##################### 
        #prepare next cycle
        nextStartTime = nextStartTime + SYSTEM_TICK_CYCLE_TIME

        #Statistics
        idleTime = nextStartTime - time.time() #this contains the sleep time shortened by the last cycle duration
        PDI.cpuLoad = 1.0 - (idleTime / SYSTEM_TICK_CYCLE_TIME)
        PDI.systemTickRunTime = SYSTEM_TICK_CYCLE_TIME - idleTime

        #write process data and prepare next cycle
        PDI.write()

        try:
            time.sleep(nextStartTime - time.time()) #sleep time by runtime of previous cycle
        except ValueError:                          #cycle time violation: skip compensation 
            print('Cycle time violation: %s'%(nextStartTime - time.time()))
            time.sleep(SYSTEM_TICK_CYCLE_TIME)  



#start cyclic system
systemTickThread = threading.Thread(target=SystemTick)
systemTickThread.start()

