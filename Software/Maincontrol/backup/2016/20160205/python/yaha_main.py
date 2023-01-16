#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import datetime, time
import threading

import core.pdi.yaha_data
import core.web_bridge.yaha_ui
import core.set_handler.yaha_set
import core.io_handler.scheduler
import core.modules.manager


SYSTEM_TICK_CYCLE_TIME = 0.2    #seconds
SYSTEM_TICK_TOLERANCE  = 0.2   #seconds

YAHA_SETTINGS_PATH = '/home/pi/Yaha/settings'
YAHA_MODULE_ROOT_PATH = '/home/pi/Yaha/modules'


def SystemTick():
    pdiPathList = []
    
    print("Yaha started at %s"%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


    #initialize system tick    
    nextStartTime = time.time()

    #create global process data image    
    PDI = core.pdi.yaha_data.ProcessDataImage()
    
    #initialize plug-in modules
    moduleManager = core.modules.manager.main(PDI)
    moduleManager.createYahaModuleList(YAHA_MODULE_ROOT_PATH)
    moduleManager.initializeYahaModules()
    pdiPathList = moduleManager.getPathListToPDI()
    for path in pdiPathList:
        PDI.addItemsFromFile(path)

    ioManager = core.io_handler.scheduler.main(PDI)
    uiServer = core.web_bridge.yaha_ui.Server()

    setManager = core.set_handler.yaha_set.main(YAHA_SETTINGS_PATH, PDI)
 
    while True:
        uiServer.update()
        PDI.read()
        ioManager.readInputs()

        ''' REZEPT HANDLING neu machen        
        PDI.cmdSaveRcp = recipeManager.saveHandler(PDI.cmdSaveRcp, PDI.rcpNameSelector)
        PDI.cmdCreateRcp = recipeManager.createHandler(PDI.cmdCreateRcp, PDI.newRcpName, PDI.read)
        PDI.cmdLoadRcp = recipeManager.loadHandler(PDI.cmdLoadRcp, PDI.rcpNameSelector, PDI.read)
        PDI.rcpNameList = recipeManager.listHandler()
        '''
        
        #################### BEGIN OF MODULE EXECUTION #################### 
        moduleManager.updateYahaModules()
        ##################### END OF MODULE EXECUTION ##################### 

        #prepare next cycle
        nextStartTime = nextStartTime + SYSTEM_TICK_CYCLE_TIME

        #Statistics
        idleTime = nextStartTime - time.time() #this contains the sleep time shortened by the last cycle duration
        PDI.cpuLoad = 1.0 - (idleTime / SYSTEM_TICK_CYCLE_TIME)
        PDI.systemTickRunTime = SYSTEM_TICK_CYCLE_TIME - idleTime

        #write process data and prepare next cycle
        ioManager.writeOutputs()
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

