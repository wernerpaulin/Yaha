#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py

import datetime, time
import threading
import sys

import core.pdi.yaha_pdi
import core.web_bridge.yaha_ui
import core.io_handler.scheduler
import core.modules.manager

SYSTEM_TICK_CYCLE_TIME = 0.1    #seconds
SYSTEM_TICK_TOLERANCE  = 0.2   #seconds

YAHA_PDI_REMANENT_DATA_PATH = '/home/pi/Yaha/rem_data/rem_data.xml'

def SystemTick():
    pdiPathList = []
    
    print("Yaha started at %s"%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    #create global process data image    
    PDI = core.pdi.yaha_pdi.ProcessDataImage(YAHA_PDI_REMANENT_DATA_PATH)
   
    #initialize plug-in modules
    moduleManager = core.modules.manager.main(PDI)
    ioManager = core.io_handler.scheduler.main(PDI)
    uiServer = core.web_bridge.yaha_ui.Server(PDI)

    PDI.write()     #write modified PDI values back to data base before cylic part starts: necessary because remanent value override during init of moduleManager()

    #initialize system tick    
    nextStartTime = time.time()
    while True:
        #back door to stop script in case terminal won't work anymore
        if (PDI.cmdStopSystem == 1):
            print("Forced shutdown of Yaha system")
            sys.exit("Forced shutdown of Yaha system")
            break;
        
        uiServer.update()
        PDI.read()

        ioManager.readInputs()
        
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
            #plausibility check if time has been set backward
            if (nextStartTime - time.time() < SYSTEM_TICK_CYCLE_TIME):
                time.sleep(nextStartTime - time.time()) #sleep time by runtime of previous cycle
            else:
                print("Cycle time jitter due to time manipulation")
                nextStartTime = time.time() + SYSTEM_TICK_CYCLE_TIME    #reinitialize time measurement
                time.sleep(SYSTEM_TICK_CYCLE_TIME)
                
        except:                          #cycle time violation: skip compensation 
            print('Cycle time violation: %s'%(nextStartTime - time.time()))
            nextStartTime = time.time() + SYSTEM_TICK_CYCLE_TIME + SYSTEM_TICK_TOLERANCE    #reinitialize time measurement
            time.sleep(SYSTEM_TICK_CYCLE_TIME + SYSTEM_TICK_TOLERANCE) #allow temporarily a tolerance to overcome cycle time violation 



#start cyclic system
systemTickThread = threading.Thread(target=SystemTick)
systemTickThread.start()

