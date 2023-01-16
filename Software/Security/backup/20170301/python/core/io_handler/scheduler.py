#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python3 /home/pi/Yaha/yaha_main.py

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

try:
    import Modbus.driver
except Exception as e:
    pass
    #print("Error io scheduler: {0}".format(e))

try:
    import y2y.client
except Exception as e:
    pass
    #print("Error import io scheduler: {0}".format(e))



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
        
        try:
            self.ioDriverList['MODBUS'] = Modbus.driver.main(self.PDI)
        except Exception as e:
            pass
            #print("Error io scheduler: {0}".format(e))
        
        try:
            self.ioDriverList['Y2Y'] = y2y.client.main(self.PDI)
        except Exception as e:
            pass
            #print("Error io scheduler: {0}".format(e))
        
      
    def readInputs(self):
        #loop through all registered drivers and activate read function
        for driver in self.ioDriverList:
            self.ioDriverList[driver].readInputs()
  
    
    def writeOutputs(self):
        #loop through all registered drivers and activate write function
        for driver in self.ioDriverList:
            self.ioDriverList[driver].writeOutputs()
  

