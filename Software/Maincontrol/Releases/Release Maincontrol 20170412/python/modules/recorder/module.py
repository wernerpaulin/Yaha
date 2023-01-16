#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import os
import sys
import xml.etree.ElementTree as xmlParser
import datetime, time
import csv
import shutil
from decimal import Decimal

MODULE_CFG_FILE_NAME = "module.cfg.xml"
RECORD_CONTAINER_CFG_ELEMENT_NAME = "./recordcontainers/recordcontainer"
DATAITEM_ELEMENT_NAME = "dataitem"
FIELD_NAME_DATE_TIME_STAMP = "date"     #mandatory for chart function in javascript
FILE_NAME_SUFFIX = ".csv"
WWW_LOGS_DST_PATH = "/var/www/yaha/logs/"

REC_STATE_RECORDING = 0
REC_STATE_STOPPED = 1

def init(PDI):
    global RecordContainers
    RecordContainers = dict()
    attrList = []
    containerID = 0
    
    #read module configuration and initialize each device
    try:
        cfgFile = os.path.dirname(__file__) + '/' + MODULE_CFG_FILE_NAME
        cfgTree = xmlParser.parse(cfgFile)
        cfgRoot = cfgTree.getroot()

        #read configuration of switches
        for recordContainerCfg in cfgRoot.findall(RECORD_CONTAINER_CFG_ELEMENT_NAME):
            try:
                #set up a switch manager for each switch found in the configuration
                containerID = recordContainerCfg.get('id')
                RecordContainers[containerID] = recordManager(PDI, containerID)
                RecordContainers[containerID].interval = float(recordContainerCfg.attrib['interval'])
                RecordContainers[containerID].fileNameTrunk = recordContainerCfg.attrib['filenametrunk']
                RecordContainers[containerID].directory = recordContainerCfg.attrib['directory']
                RecordContainers[containerID].fileNameOption = recordContainerCfg.attrib['filenameoption']


                #optional parameters
                try:
                    RecordContainers[containerID].calcTimeBase = float(recordContainerCfg.attrib['calcTimeBase'])
                except:
                    RecordContainers[containerID].calcTimeBase = 0
                    
                try:
                    RecordContainers[containerID].nbMaxDataRecords = float(recordContainerCfg.attrib['nbMaxDataRecords'])
                except:
                    RecordContainers[containerID].nbMaxDataRecords = 0

                try:
                    RecordContainers[containerID].pdiTagStart = recordContainerCfg.attrib['startCmdTag']
                    RecordContainers[containerID].pdiTagStop = recordContainerCfg.attrib['stopCmdTag']
                    RecordContainers[containerID].pdiTagClear = recordContainerCfg.attrib['clearCmdTag']
                except:
                    RecordContainers[containerID].pdiTagStart = ""
                    RecordContainers[containerID].pdiTagStop = ""
                    RecordContainers[containerID].pdiTagClear = ""

                #initialize record container data
                dataItemCfg = recordContainerCfg.find('.//dataitems')
                dataItemList = dataItemCfg.findall(DATAITEM_ELEMENT_NAME)
                for dataItem in dataItemList:
                    RecordContainers[containerID].dataItems[dataItem.attrib['name']] = recordDataItem()
                    RecordContainers[containerID].dataItems[dataItem.attrib['name']].pdiTag = dataItem.attrib['pditag']
                    
                    try:
                        RecordContainers[containerID].dataItems[dataItem.attrib['name']].calcFunction = dataItem.attrib['calculation']
                        #initialize average calculation
                        if (RecordContainers[containerID].dataItems[dataItem.attrib['name']].calcFunction == "avg"):
                            RecordContainers[containerID].dataItems[dataItem.attrib['name']].nbMaxAvgDataRecords = int(RecordContainers[containerID].interval / RecordContainers[containerID].calcTimeBase) + 1
                            RecordContainers[containerID].dataItems[dataItem.attrib['name']].avgDataRecords = [dict() for x in range(RecordContainers[containerID].dataItems[dataItem.attrib['name']].nbMaxAvgDataRecords)]
                    except:
                        RecordContainers[containerID].dataItems[dataItem.attrib['name']].calcFunction = None
                    
                    try:
                        RecordContainers[containerID].dataItems[dataItem.attrib['name']].decimalPlaces = int(dataItem.attrib['decimalplaces'])
                    except:
                        RecordContainers[containerID].dataItems[dataItem.attrib['name']].decimalPlaces = None

            except Exception, e:
                print("Loading configuration for record container {0} failed in line: {1}: {2}".format(containerID, sys.exc_info()[-1].tb_lineno, e))
                return    

    except Exception, e:
        print("Loading recorder configuration failed in line: {0}: {1}".format(sys.exc_info()[-1].tb_lineno, e))
        return
   

def update(PDI):
    global RecordContainers

    for rc in RecordContainers:
        #user interface (PDI)
        try:
            #start recorder 
            if (getattr(PDI, RecordContainers[rc].pdiTagStart) == 1):
                setattr(PDI, RecordContainers[rc].pdiTagStart, 0)
                RecordContainers[rc].recordingState = REC_STATE_RECORDING
                RecordContainers[rc].lastRecordTimestamp = 0        #start recording immediately

            #stop recorder 
            if (getattr(PDI, RecordContainers[rc].pdiTagStop) == 1):
                setattr(PDI, RecordContainers[rc].pdiTagStop, 0)
                RecordContainers[rc].recordingState = REC_STATE_STOPPED

            #clear current file 
            if (getattr(PDI, RecordContainers[rc].pdiTagClear) == 1):
                setattr(PDI, RecordContainers[rc].pdiTagClear, 0)
                try:
                    os.remove(RecordContainers[rc].currentRecordFile)
                    RecordContainers[rc].saveDataRecord()       #write immediately one record to force update the web server file
                except Exception, e:
                    print("Clear file failed: {0}".format(e))

        except:
            pass

        #stop recording of maximum number of records have been already recorded - "0" as maximum number deactivates this check 
        if (RecordContainers[rc].nbMaxDataRecords > 0) and (RecordContainers[rc].nbDataRecords > RecordContainers[rc].nbMaxDataRecords):
            RecordContainers[rc].recordingState = REC_STATE_STOPPED

        #skip this recorder instance if it is not recording
        if (RecordContainers[rc].recordingState != REC_STATE_RECORDING):
            continue
        
        #sample data for average calculation
        if ( (time.time() - RecordContainers[rc].lastCalcRecordTimestamp) >= RecordContainers[rc].calcTimeBase):
            RecordContainers[rc].lastCalcRecordTimestamp = time.time()
            RecordContainers[rc].calcDataRecord()
        
        
        #check each recorder instance whether it is time to save a record
        if ( (time.time() - RecordContainers[rc].lastRecordTimestamp) >= RecordContainers[rc].interval):
            RecordContainers[rc].lastRecordTimestamp = time.time()
            RecordContainers[rc].saveDataRecord()
            

class recordManager:
    #init
    def __init__(self, PDI, containerID):
        self.containerID = containerID
        self.PDI = PDI
        self.interval = 0
        self.calcTimeBase = 0
        self.directory = ""
        self.fileNameTrunk = ""
        self.fileNameOption = ""
        self.currentRecordFile = ""
        self.lastRecordTimestamp = 0
        self.lastCalcRecordTimestamp = 0
        self.dataItems = dict()
        self.nbMaxDataRecords = 0
        self.pdiTagStart = ""
        self.pdiTagStop = ""
        self.pdiTagClear = ""
        self.recordingState = REC_STATE_RECORDING
        self.nbDataRecords = 0
        self.currentDataRecord = dict()
        
        self.saveDataRecord()
    
    def calcDataRecord(self):
        #add sampling data to average calculation buffer and generate average value
        for dataItem in self.dataItems:
            if (self.dataItems[dataItem].calcFunction == "avg"):
                #stop adding data if number nbMaxAvgDataRecords exceeded
                if (self.dataItems[dataItem].cntAvgDataRecords < self.dataItems[dataItem].nbMaxAvgDataRecords):
                    #add time stamp
                    self.dataItems[dataItem].avgDataRecords[self.dataItems[dataItem].cntAvgDataRecords][FIELD_NAME_DATE_TIME_STAMP] = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
                    
                    try:
                        self.dataItems[dataItem].avgDataRecords[self.dataItems[dataItem].cntAvgDataRecords][dataItem] = getattr(self.PDI, self.dataItems[dataItem].pdiTag)
                        self.dataItems[dataItem].cntAvgDataRecords = self.dataItems[dataItem].cntAvgDataRecords + 1
                    except Exception, e:
                        print("Getting value of PDI tag <{0}> failed: {1}".format(self.dataItems[dataItem].pdiTag, e))
        
    
    def saveDataRecord(self):
        #delete old records
        self.currentDataRecord.clear()
        
        #add time stamp
        self.currentDataRecord[FIELD_NAME_DATE_TIME_STAMP] = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        
        #add current PDI values of all configured data
        for dataItem in self.dataItems:
            #record average value if data item is configured for average
            if (self.dataItems[dataItem].calcFunction == "avg") and (self.dataItems[dataItem].cntAvgDataRecords > 0):
                #sum up all values
                self.currentDataRecord[dataItem] = 0
                recordIndex = 0
                while (recordIndex < self.dataItems[dataItem].cntAvgDataRecords):
                    #print(self.dataItems[dataItem].avgDataRecords[recordIndex])
                    self.currentDataRecord[dataItem] = self.currentDataRecord[dataItem] + self.dataItems[dataItem].avgDataRecords[recordIndex][dataItem]
                    
                    recordIndex = recordIndex + 1

                #divide by number of samples to get average value                
                self.currentDataRecord[dataItem] = float(self.currentDataRecord[dataItem]) / self.dataItems[dataItem].cntAvgDataRecords  
                
                #reset average buffer data count
                self.dataItems[dataItem].cntAvgDataRecords = 0
                #reset list with records by creating a new list with empty dict()
                self.dataItems[dataItem].avgDataRecords = [dict() for x in range(self.dataItems[dataItem].nbMaxAvgDataRecords)]
            else:
                try:
                    self.currentDataRecord[dataItem] = getattr(self.PDI, self.dataItems[dataItem].pdiTag)
                except Exception, e:
                    print("Getting value of PDI tag <{0}> failed: {1}".format(self.dataItems[dataItem].pdiTag, e))

            #round data item value
            if (self.dataItems[dataItem].decimalPlaces != None):
                #convert float to decimal
                self.currentDataRecord[dataItem] = Decimal(self.currentDataRecord[dataItem])
                #round to number decimal places
                self.currentDataRecord[dataItem] = round(self.currentDataRecord[dataItem], self.dataItems[dataItem].decimalPlaces)


        if (self.fileNameOption.lower() == "%y"):
            fileNameOptionString = "_" + str(datetime.date.today().year)         #e.g. add _2016 to year
        else:
            fileNameOptionString = ""

        self.currentRecordFile = self.directory + self.fileNameTrunk + fileNameOptionString + FILE_NAME_SUFFIX   

        try:
            with open(self.currentRecordFile, 'a') as csvfile:
                #create list with field names
                fieldnames = []
                for recordItem in self.currentDataRecord:
                    fieldnames.append(recordItem)
                
                #sort fields alphabetically
                fieldnames = sorted(fieldnames, key=str.lower)
                #move DateTime Stamp to front
                fieldnames.insert(0, fieldnames.pop(fieldnames.index(FIELD_NAME_DATE_TIME_STAMP)))
    
                #create writer handler
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
      
                #write header if file is new
                if ( os.path.getsize(self.currentRecordFile) == 0):
                    #print("write header")
                    writer.writeheader()
                
                #write record
                writer.writerow(self.currentDataRecord)
    
                csvfile.close()
    
            #copy file to www directory for webserver access
            shutil.copy(self.currentRecordFile, WWW_LOGS_DST_PATH)
                
            #update number of data records        
            self.nbDataRecords = sum(1 for line in open(self.currentRecordFile))
        except Exception, e:
            print('Saving recording data failed: ' + str(e))


class recordDataItem:
    #init
    def __init__(self):
        self.pdiTag = None
        self.calcFunction = None
        self.avgDataRecords = []
        self.nbMaxAvgDataRecords = 0
        self.cntAvgDataRecords = 0
        self.avgValue = None
        self.decimalPlaces = None
