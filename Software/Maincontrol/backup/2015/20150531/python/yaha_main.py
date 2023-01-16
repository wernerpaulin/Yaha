#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import datetime, time
import threading
import yaha_data
import yaha_ui
import yaha_enocean
import yaha_recipe
import yaha_logic


SYSTEM_TICK_CYCLE_TIME = 0.2    #seconds
SYSTEM_TICK_TOLERANCE  = 0.2   #seconds

YAHA_PDI_DEFAULT_RECIPE = '/home/pi/Yaha/pdi/yaha_pdi_default.rcp.xml'
#YAHA_RECIPE_PATH = 'C:/Users/paulinw/Desktop/Home Automation/Yaha/backup/trunk/python/pdi'
YAHA_RECIPE_PATH = '/home/pi/Yaha/pdi'

def SystemTick():
    #initialize system tick    
    nextStartTime = time.time()
    PDI = yaha_data.ProcessDataImage(YAHA_PDI_DEFAULT_RECIPE)
    uiServer = yaha_ui.Server()
    enoceanDriver = yaha_enocean.Driver()
    recipeManager = yaha_recipe.Manager(YAHA_RECIPE_PATH)

    while True:
        enoceanDriver.update()
        uiServer.update()
        PDI.read()
                
        PDI.cmdSaveRcp = recipeManager.saveHandler(PDI.cmdSaveRcp, PDI.rcpNameSelector)
        PDI.cmdCreateRcp = recipeManager.createHandler(PDI.cmdCreateRcp, PDI.newRcpName, PDI.read)
        PDI.cmdLoadRcp = recipeManager.loadHandler(PDI.cmdLoadRcp, PDI.rcpNameSelector, PDI.read)
        PDI.rcpNameList = recipeManager.listHandler()

        ############## APPLICATION SPECIFIC CODE
        yaha_logic.YahaCyclicLogic(PDI)
        
        #update information from Enocean and other I/O drivers
        PDI.logEnocean = enoceanDriver.logEnocean
        ############## APPLICATION SPECIFIC CODE


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
        except:                          #cycle time violation: skip compensation 
            print('Cycle time violation: %s'%(nextStartTime - time.time()))
            nextStartTime = time.time() + SYSTEM_TICK_CYCLE_TIME + SYSTEM_TICK_TOLERANCE    #reinitalize time measurement
            time.sleep(SYSTEM_TICK_CYCLE_TIME + SYSTEM_TICK_TOLERANCE) #allow temporarily a tolerance to overcome cycle time violation 



#start cyclic system
systemTickThread = threading.Thread(target=SystemTick)
systemTickThread.start()

