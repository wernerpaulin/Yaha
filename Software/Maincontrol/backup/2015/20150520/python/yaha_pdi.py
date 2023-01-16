#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import xml.etree.ElementTree as xmlParser
import os

#/home/pi/Yaha/yaha_pdi.xml
def YahaPDIcreate(file):
    global YahaPDIcursor
    global YahaPDIdb

    # Create a database in RAM
    YahaPDIdb = sqlite3.connect(':memory:')
    
    # Get a cursor object
    YahaPDIcursor = YahaPDIdb.cursor()
    YahaPDIcursor.execute('''CREATE TABLE yaha_pdi(
                                                  id INTEGER PRIMARY KEY, 
                                                  processTag TEXT, 
                                                  uiTag TEXT,
                                                  valueType TEXT,
                                                  valueREAL REAL,
                                                  valueTEXT TEXT,
                                                  domain TEXT,
                                                  owner TEXT,
                                                  deviceID TEXT,
                                                  uiMode TEXT,
                                                  lowREAL REAL,
                                                  highREAL REAL,
                                                  zone TEXT,
                                                  subzone TEXT,
                                                  room TEXT,
                                                  ioType TEXT)''')
    YahaPDIdb.commit()
    
    #get access to data base
    YahaPDIcursor = YahaPDIdb.cursor()

    #read process data image configuration from xml file
    pdiRecord = {'empty': 0}    #force creating a dictionary
    pdiRecord.clear()           #clear dictionary immediately
    pdiTree = xmlParser.parse(file)
    pdiRoot = pdiTree.getroot()
    
    #walk through all process data elements in process data image
    for pdiTag in pdiRoot:
        #read out all properties (= sub children) into a dictionary
        pdiRecord.clear()   #clear dictionary from data from last loop
        for property in pdiTag:
            pdiRecord[property.tag] = property.text     #e.g.: processTag : 'switch1'
    
        # Insert dictionary into process data image
        YahaPDIcursor.execute('''INSERT INTO yaha_pdi( processTag, 
                                                       uiTag, 
                                                       valueType, 
                                                       valueREAL, 
                                                       valueTEXT,
                                                       domain, 
                                                       owner, 
                                                       deviceID, 
                                                       uiMode, 
                                                       lowREAL, 
                                                       highREAL, 
                                                       zone, 
                                                       subzone,
                                                       room,
                                                       ioType )
                                  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', 
                                  (pdiRecord['processTag'],
                                   pdiRecord['uiTag'],
                                   pdiRecord['valueType'],
                                   pdiRecord['valueREAL'],
                                   pdiRecord['valueTEXT'],
                                   pdiRecord['domain'],
                                   pdiRecord['owner'],
                                   pdiRecord['deviceID'],
                                   pdiRecord['uiMode'],
                                   pdiRecord['lowREAL'],
                                   pdiRecord['highREAL'],
                                   pdiRecord['zone'],
                                   pdiRecord['subzone'],
                                   pdiRecord['room'],
                                   pdiRecord['ioType'],))
        
        YahaPDIdb.commit()

def YahaPDIshutDown():
    # Close the db connection
    YahaPDIdb.close()

#write data give as dictionary into PDI
def YahaPDIwriteValue(processTags, uiTags):
    tagListToWrite = {'empty': 0}    #force creating a dictionary
    tagListToWrite.clear()           #clear dictionary immediately

    #find out which tags are given (priority is on process tags)
    #copy to a new dictionary to avoid double code sections below
    if len(processTags) > 0:
        tagsToWrite = processTags.copy()
        tagColumnName = "processTag"        #used for dynamic column selection
    elif len(uiTags) > 0:
        tagsToWrite = uiTags.copy()
        tagColumnName = "uiTag"             #used for dynamic column selection
    else:                                   #no tag list given at all
        return tagListToWrite

    #write tag values in dictionary (either processTags or uiTags)
    for tag in tagsToWrite:
        #1. Check whether tag exists in PDI and in case of tags from UI it's allowed to write
        if (tagColumnName == "processTag"):
            YahaPDIcursor.execute('''SELECT''' + " " + tagColumnName + ''', valueType, valueREAL, valueTEXT, lowREAL, highREAL FROM yaha_pdi WHERE''' + " " + tagColumnName + " " + '''= ? ''', (tag,))
        else:
            YahaPDIcursor.execute('''SELECT''' + " " + tagColumnName + ''', valueType, valueREAL, valueTEXT, lowREAL, highREAL FROM yaha_pdi WHERE''' + " " + tagColumnName + " " + '''= ? AND (uiMode = "w" or uiMode = "rw")''', (tag,))
        
        processTag = 0
        valueType = 1
        valueREAL = 2
        valueTEXT = 3
        lowREAL = 4
        highREAL = 5
        
        #2. Assume tags are unique -> get only first
        record = YahaPDIcursor.fetchone()

        if record is None:
            print('Tag %s was either read only or not found'%(tag))
        else:
            #3. limit give value if required and write value into PDI
            if (record[valueType] == "REAL"): 
                try:
                    tagsToWrite[tag] = max(min(float(tagsToWrite[tag]), record[5]), record[4])   #force casting to float as JSON transports values as string
                except ValueError:
                    print('Value can not be concerted to float: %s'%(tagsToWrite[tag]))                
               
                YahaPDIcursor.execute('''UPDATE yaha_pdi SET valueREAL = ? WHERE''' + " " + tagColumnName + ''' = ? ''',(tagsToWrite[tag], tag))
            elif (record[valueType] == "TEXT"):
               YahaPDIcursor.execute('''UPDATE yaha_pdi SET valueTEXT = ? WHERE''' + " " + tagColumnName + ''' = ? ''',(tagsToWrite[tag], tag))
               YahaPDIdb.commit()
            else:
                print('Data type not supported: %s'%(record[valueType]))

    #return dict which now includes values which were limited during writing
    return tagsToWrite 


#write data give as dictionary into PDI
def YahaPDIreadValue(processTags, uiTags):
    tagsToRead = {'empty': 0}    #force creating a dictionary
    tagsToRead.clear()           #clear dictionary immediately

    #find out which tags are given (priority is on process tags)
    #copy to a new dictionary to avoid double code sections below
    if len(processTags) > 0:
        tagsToRead = processTags.copy()
        tagColumnName = "processTag"        #used for dynamic column selection
    elif len(uiTags) > 0:
        tagsToRead = uiTags.copy()
        tagColumnName = "uiTag"             #used for dynamic column selection
    else:                                   #no tag list given at all
        return tagsToRead

    #write tag values in dictionary (either processTags or uiTags)
    for tag in tagsToRead:
        #1. Check whether tag exists in PDI and in case of ui-tag is configured to read
        if (tagColumnName == "processTag"):
            YahaPDIcursor.execute('''SELECT''' + " " + tagColumnName + ''', valueType, valueREAL, valueTEXT FROM yaha_pdi WHERE''' + " " + tagColumnName + " " + '''= ? ''', (tag,))
        else:
            YahaPDIcursor.execute('''SELECT''' + " " + tagColumnName + ''', valueType, valueREAL, valueTEXT FROM yaha_pdi WHERE''' + " " + tagColumnName + " " + '''= ? AND (uiMode = "r" or uiMode = "rw")''', (tag,))

        processTag = 0
        valueType = 1
        valueREAL = 2
        valueTEXT = 3

        
        #2. Assume tags are unique -> get only first
        record = YahaPDIcursor.fetchone()
        
        if record is None:
            print('Tag %s was either write only or not found'%(tag))
        else:
            #3. limit give value if required and write value into PDI
            if (record[valueType] == "REAL"):   
               tagsToRead[tag] = record[valueREAL]
            elif (record[valueType] == "TEXT"):
               tagsToRead[tag] = record[valueTEXT]
            else:
                print('Data type not supported: %s'%(record[valueType]))

    #return dict which includes all read values
    return tagsToRead 

#write defined value to a tags with a certain io type in a certain location
def YahaPDIwriteBroadcast(ioType, zone, subzone, room, value):
    tagListToWrite = {'empty': 0}    #force creating a dictionary
    tagListToWrite.clear()           #clear dictionary immediately

    #get all process tags match with the requested io type and location
    if len(room) > 0:   #zone, subzone has to be specified as well (rooms with same name, only need to be unique within a subzone)
        YahaPDIcursor.execute('''SELECT processTag FROM yaha_pdi WHERE ioType = ? AND zone = ? AND subzone = ? AND room = ?''', (ioType,zone,subzone,room,))
    elif len(subzone) > 0:  #zone has to be specified as well (subzones with same name, only need to be uique within a zone)
        YahaPDIcursor.execute('''SELECT processTag FROM yaha_pdi WHERE ioType = ? AND zone = ? AND subzone = ?''', (ioType,zone,subzone,))
    elif len(zone) > 0:     #zone must be unique
        YahaPDIcursor.execute('''SELECT processTag FROM yaha_pdi WHERE ioType = ? AND zone = ?''', (ioType,zone,))
    else:                   #if no specific location given update all io types
        YahaPDIcursor.execute('''SELECT processTag FROM yaha_pdi WHERE ioType = ?''', (ioType,))

    records = YahaPDIcursor.fetchall()
    processTag = 0

    for record in records:
        tagListToWrite[record[processTag]] = value
        tagListToWrite = YahaPDIwriteValue(tagListToWrite,{})

    return tagListToWrite

#get list of all processTags in PDI definition
def YahaGetProcessTagListWithValue():
    processTagList = {'empty': 0}    #force creating a dictionary
    processTagList.clear()           #clear dictionary immediately

    YahaPDIcursor.execute('''SELECT processTag, valueType, valueREAL, valueTEXT FROM yaha_pdi''')
    records = YahaPDIcursor.fetchall()

    processTag = 0
    valueType = 1
    valueREAL = 2
    valueTEXT = 3
    
    if records is None:
        print('No process tags found')
    else:
        for record in records:
            if (record[valueType] == "REAL"):   
               processTagList[record[processTag]] = record[valueREAL]
            elif (record[valueType] == "TEXT"):
               processTagList[record[processTag]] = record[valueTEXT]
            else:
                print('Data type not supported: %s'%(record[valueType]))
                 
    return(processTagList)
    

#get list of recipe files in a certain directory: *.rcp, *.rcp.xml
def YahaGetRcpFileList(path):
    rcpFileList = []
    
    for dirname, dirnames, filenames in os.walk(path):
        #dirname: current directory
        #dirnames: directories in current directory
        #filenames: file in current directory
        for filename in filenames:
            #get extension of file
            if (filename.split('.')[1] == 'rcp'):
                #add all receipe 
                rcpFileList.append(os.path.join(dirname, filename))
            else:
                continue
        break   #search only top directory (remove break to walk also all sub folders    
    
    return rcpFileList


def YahaLoadRecipe(file):
    #reads recipe data from xml file and 
    rcpData = {'empty': 0}    #force creating a dictionary
    rcpData.clear()           #clear dictionary immediately
    rcpTree = xmlParser.parse(file)
    rcpRoot = rcpTree.getroot()
    
    #walk through all process data elements in recipe
    for rcpTag in rcpRoot:
        tagName, tagValue, tagValueType = 0,0,0     #avoid any old value from previous record in case an element is not given
        #read out all properties (= sub children) into a dictionary
        for property in rcpTag:
            #in case apply is true use process tag otherwise just copy it to ui-tags
            if (apply == True):
                if (property.tag == 'processTag'):
                    tagName = property.text
            else:
                if (property.tag == 'uiTag'):
                    tagName = property.text

            if (property.tag == 'value'):
                tagValue = property.text
            elif (property.tag == 'valueType'):
                tagValueType = property.text

        #xml is per default text. In case a real value has been read force conversion to real
        if (tagValueType == 'REAL'):
            tagValue = float(tagValue)

        rcpData[tagName] = tagValue     #build dictionary (e.g.: setTempFelix: 11.0)
    
        YahaPDIwriteValue(rcpData, {})        #write process tags
    return


class clYaha_pdi:
    'Yaha Process Data Image: simplifies handing central process data by using class attributes instead of dictionary strings'

    def __init__(self, pdiDefinitionFile):
        #create Process Data Image
        YahaPDIcreate(pdiDefinitionFile)
        #get all listed process tags
        self._processTagList = YahaGetProcessTagListWithValue()
        #dynamically add process tags to class as attributes
        for tag in self._processTagList:
            setattr(self, tag, self._processTagList[tag])

        #if further attributes are created they will be ignored as process data but can be used in the code

    def read(self):
        processTags = {'empty': 0}    #force creating a dictionary
        processTags.clear()           #clear dictionary immediately

        #convert list into dictionary for PDI read
        for tag in self._processTagList:
            processTags[tag] = "$read"

        #read process variables from PDI
        processTags = YahaPDIreadValue(processTags, {})

        #set class variables with values from PDI
        for tag in processTags:
            setattr(self, tag, processTags[tag])

    def write(self):
        processTags = {'empty': 0}    #force creating a dictionary
        processTags.clear()           #clear dictionary immediately

        #convert class variables into dictionary for PDI write
        for tag in self._processTagList:
            processTags[tag] = getattr(self, tag)

        #write process variables from PDI
        YahaPDIwriteValue(processTags, {})
        

############################################# TEST TEST TEST TEST TEST TEST TEST /Begi ######################################
#YahaPDIcreate('/home/pi/Yaha/yaha_pdi.xml')
#YahaPDIcreate('C:/Users/paulinw/Desktop/Home Automation/Yaha/backup/trunk/python/pdi/yaha_pdi.xml')
#print(YahaGetProcessTagListWithValue())

#processTagList = {}
#processTagList['setTempFelix']    = 50.3
#processTagList['setTempTheo']    = 22.2
#processTagList['logEnocean']    = "Hello World"
#processTagList['tempParentBathroom'] = 10.0

#uiTagList = {}
#uiTagList['uiSetTempFelix'] = 34.3
#uiTagList['uiSetTempTheo'] = 25.5
#uiTagList['uiLogEnocean'] = "Test"
#uiTagList['uiTempParentBathroom'] = 0


#broadCastResultList = YahaPDIwriteBroadcast("light", "", "", "", 0.0)    #swtiches off all lights
#print(YahaPDIreadValue(broadCastResultList,{}))


#tagListWritten = YahaPDIwriteValue(processTagList,uiTagList)
#print(tagListWritten)

#print(YahaPDIreadValue(processTagList,{}))
#print(YahaPDIreadValue({},uiTagList))

#rcpFileList = YahaGetRcpFileList('C:/Users/paulinw/Desktop/Home Automation/Yaha/backup/trunk/python')
#YahaLoadRecipe(rcpFileList[0], apply = False)

#YahaPDIwriteValue({},uiTagList)


#YahaPDIshutDown();




############################################# TEST TEST TEST TEST TEST TEST TEST /Begi ######################################



    

