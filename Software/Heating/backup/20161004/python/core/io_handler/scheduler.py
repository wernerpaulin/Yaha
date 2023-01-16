#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

try:
    import enocean.protocol.driver
except:
    pass

try:
    import ABE.driver
except Exception as e:
    pass
    #print("Error: {0}".format(e))

try:
    import GPIO_board.driver
except:
    pass

class main():
    "IO scheduler"
    def __init__(self, PDI):
        self.PDI = PDI
        self.ioDriverList = dict()
         
        #initialize all supported IO drivers:
        try:
            self.ioDriverList['enocean'] = enocean.protocol.driver.main(self.PDI)
        except:
            pass

        try:
            self.ioDriverList['ABE'] = ABE.driver.main(self.PDI)
        except Exception as e:
            pass
            #print("Error: {0}".format(e))
        
        try:
            self.ioDriverList['GPIO'] = GPIO_board.driver.main(self.PDI)
        except:
            pass
        
      
    def readInputs(self):
        #loop through all registered drivers and activate read function
        for driver in self.ioDriverList:
            self.ioDriverList[driver].readInputs()
  
    
    def writeOutputs(self):
        #loop through all registered drivers and activate write function
        for driver in self.ioDriverList:
            self.ioDriverList[driver].writeOutputs()
  

