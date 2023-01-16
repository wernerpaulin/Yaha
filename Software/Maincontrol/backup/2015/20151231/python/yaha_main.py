#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import datetime, time
import threading

import core.pdi.yaha_data
import core.web_bridge.yaha_ui
import core.recipe.yaha_recipe
import core.io_handler.scheduler
import core.dt_handler.yaha_datetime


import core.standard_devices.manager



SYSTEM_TICK_CYCLE_TIME = 0.2    #seconds
SYSTEM_TICK_TOLERANCE  = 0.2   #seconds

YAHA_PDI_DEFAULT_RECIPE = '/home/pi/Yaha/core/pdi/yaha_pdi_default.rcp.xml'
YAHA_RECIPE_PATH = '/home/pi/Yaha/core/pdi'


def SystemTick():
    print("Yaha started at %s"%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    #initialize system tick    
    nextStartTime = time.time()
    
    #initialize data which keep their values while Yaha is running
    PDI = core.pdi.yaha_data.ProcessDataImage(YAHA_PDI_DEFAULT_RECIPE)
    uiServer = core.web_bridge.yaha_ui.Server()
    recipeManager = core.recipe.yaha_recipe.Manager(YAHA_RECIPE_PATH)
    ioManager = core.io_handler.scheduler.main(PDI)
    sdManager = core.standard_devices.manager.main(PDI)
    dateTimeManager = core.dt_handler.yaha_datetime.Manager()

    while True:
        uiServer.update()
        PDI.read()
        ioManager.readInputs()
                
        PDI.cmdSaveRcp = recipeManager.saveHandler(PDI.cmdSaveRcp, PDI.rcpNameSelector)
        PDI.cmdCreateRcp = recipeManager.createHandler(PDI.cmdCreateRcp, PDI.newRcpName, PDI.read)
        PDI.cmdLoadRcp = recipeManager.loadHandler(PDI.cmdLoadRcp, PDI.rcpNameSelector, PDI.read)
        PDI.rcpNameList = recipeManager.listHandler()
        PDI.cmdSetDateTime = dateTimeManager.setDateTimeHandler(PDI.cmdSetDateTime, PDI.setDateString, PDI.setTimeString)
        PDI.currentYear, PDI.currentMonth, PDI.currentDay = dateTimeManager.getDate()
        PDI.currentHour, PDI.currentMinute, PDI.currentSecond = dateTimeManager.getTime()

        #################### BEGIN OF CYCLIC CODE #################### 
        PDI.count1 = PDI.count1 + 1
        #PDI.var1 = PDI.var1 + 1
        #PDI.var2 = PDI.var2 + 1
        #PDI.var3 = PDI.var3 + 1

        PDI.selectText = PDI.selectGroup #selectStandard

  
        #print(PDI.checkboxgroup1)
        #print(PDI.checkboxgroup2)

        if (PDI.checkboxgroup1 == 1.0):
            PDI.checkboxgroup2 = 1.0
     
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
        ioManager.writeOutputs()
        sdManager.update()
        PDI.write()

        try:
            time.sleep(nextStartTime - time.time()) #sleep time by runtime of previous cycle
        except:                          #cycle time violation: skip compensation 
            print('Cycle time violation: %s'%(nextStartTime - time.time()))
            nextStartTime = time.time() + SYSTEM_TICK_CYCLE_TIME + SYSTEM_TICK_TOLERANCE    #reinitialize time measurement
            time.sleep(SYSTEM_TICK_CYCLE_TIME + SYSTEM_TICK_TOLERANCE) #allow temporarily a tolerance to overcome cycle time violation 



#start cyclic system
systemTickThread = threading.Thread(target=SystemTick)
systemTickThread.start()

