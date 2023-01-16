#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_main.py

import os
import xml.etree.ElementTree as xmlParser
import datetime, time
import csv
import shutil

MODULE_CFG_FILE_NAME = "module.cfg.xml"
RECORD_CONTAINER_CFG_ELEMENT_NAME = "./recordcontainers/recordcontainer"
DATAITEM_ELEMENT_NAME = "dataitem"
FIELD_NAME_DATE_TIME_STAMP = "date"     #mandatory for chart function in javascript
FILE_NAME_SUFFIX = ".csv"
WWW_LOGS_DST_PATH = "/var/www/yaha/logs/"

def init(PDI):
    global RecordContainers
    RecordContainers = dict()
    attrList = []
    
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
                RecordContainers[containerID] = recordManager(PDI)
                RecordContainers[containerID].containerID = containerID
    
                RecordContainers[containerID].interval = float(recordContainerCfg.attrib['interval'])
                RecordContainers[containerID].fileNameTrunk = recordContainerCfg.attrib['filenametrunk']
                RecordContainers[containerID].directory = recordContainerCfg.attrib['directory']

                #initialize record container data
                dataItemCfg = recordContainerCfg.find('.//dataitems')
                dataItemList = dataItemCfg.findall(DATAITEM_ELEMENT_NAME)
                for dataItem in dataItemList:
                    RecordContainers[containerID].dataItems[dataItem.attrib['name']] = dataItem.attrib['pditag']

            except Exception, e:
                print("Loading configuration for record container {0} failed: {1}".format(containerID, e))
                return    

    except Exception, e:
        print("Loading recorder configuration failed: {0}".format(e))
        return
   

def update(PDI):
    global RecordContainers

    for rc in RecordContainers:
        #check each recorder instance whether it is time to save a record
        if ( (time.time() - RecordContainers[rc].lastRecordTimestamp) >= RecordContainers[rc].interval):
            RecordContainers[rc].lastRecordTimestamp = time.time()
            RecordContainers[rc].saveDataRecord()
            
            #copy file to www directory for webserver access
            shutil.copy(RecordContainers[rc].currentRecordFile, WWW_LOGS_DST_PATH)


class recordManager:
    #init
    def __init__(self, PDI):
        self.containerID = None
        self.PDI = PDI
        self.interval = 0
        self.directory = ""
        self.fileNameTrunk = ""
        self.currentRecordFile = ""
        self.lastRecordTimestamp = 0
        self.dataItems = dict()
        self.currentDataRecord = dict()
    
    def saveDataRecord(self):
        #delete old records
        self.currentDataRecord.clear()
        
        #prepare record to save as dictionary
        #add time stamp
        self.currentDataRecord[FIELD_NAME_DATE_TIME_STAMP] = datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        #add current PDI values of all configured data
        for dataItem in self.dataItems:
            try:
                self.currentDataRecord[dataItem] = getattr(self.PDI, self.dataItems[dataItem])
            except Exception, e:
                print("Getting value of PDI tag <{0}> failed: {1}".format(self.dataItems[dataItem], e))

        self.currentRecordFile = self.directory + self.fileNameTrunk + "_" + str(datetime.date.today().year) + FILE_NAME_SUFFIX   #e.g. add _2016 to year

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
        
        
