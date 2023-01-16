#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python /home/pi/Yaha/yaha_data.py
#python /home/pi/Yaha/yaha_main.py

import sqlite3
import xml.etree.ElementTree as xmlParser
import os
import sys

def YahaPDIcreate():
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

def YahaPDIaddItemsFromFile(file):
    #read process data image configuration from xml file
    pdiRecord = {'empty': 0}    #force creating a dictionary
    pdiRecord.clear()           #clear dictionary immediately

    #processTagList contains processTag and its corresponding value for initializing the PDI class object with value from xml file
    pdiProcessTagInitValueList = {'empty': 0}    #force creating a dictionary
    pdiProcessTagInitValueList.clear()           #clear dictionary immediately
    
    try:
        pdiTree = xmlParser.parse(file)
        pdiRoot = pdiTree.getroot()
    except:
        #no valid file give -> return empty list
        pdiProcessTagInitValueList.clear()
        return(pdiProcessTagInitValueList)

    
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

        #prepare init value for PDI class object initialization
        if (pdiRecord['valueType'] == "REAL"):
            pdiProcessTagInitValueList[pdiRecord['processTag']] = float(pdiRecord['valueREAL']);
        elif (pdiRecord['valueType'] == "TEXT"):
            pdiProcessTagInitValueList[pdiRecord['processTag']] = pdiRecord['valueTEXT'];
        else:
            print('PDI: Data type not supported: %s'%(pdiRecord['valueType']))

    return(pdiProcessTagInitValueList)



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
                    highValue = record[highREAL]
                    lowValue  = record[lowREAL]

                    #check whether there were limits set in the configuration file -> if not set it to the current value so min/max has no effect
                    if (highValue == None):
                        highValue = float(tagsToWrite[tag])

                    if (lowValue == None):
                        lowValue = float(tagsToWrite[tag])
                    
                    tagsToWrite[tag] = max(min(float(tagsToWrite[tag]), highValue), lowValue)   #force casting to float as JSON transports values as string
                    YahaPDIcursor.execute('''UPDATE yaha_pdi SET valueREAL = ? WHERE''' + " " + tagColumnName + ''' = ? ''',(tagsToWrite[tag], tag))
                    YahaPDIdb.commit()
                except:
                    print('Value can not be converted to float: %s %s'%(tagsToWrite[tag], sys.exc_info()[0]))                
               
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

#get all different owners of PDI tags (e.g. used for IO-scheduler)
def YahaPDIgetOwners():
    ownerList = list()       #force creating a list
    del ownerList[:]   #clear list immediately

    YahaPDIcursor.execute('''SELECT owner FROM yaha_pdi''')
    records = YahaPDIcursor.fetchall()

    #set record index for better readability
    owner = 0

    if records is None:
        print('No owners found')
    else:
        for record in records:
            ownerList.append(record[owner])
                 
    return(uniquifyList(ownerList))

#removes dublicates from a given list
def uniquifyList(seq, idfun=None): 
    #http://www.peterbe.com/plog/uniqifiers-benchmark    
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


#get all standard device PDI variables (e.g. used for Standard Device Manager)
def YahaPDIgetStandardDeviceTags():
    tagList = dict()       #force creating a dictionary
    tagList.clear()

    YahaPDIcursor.execute("SELECT processTag, ioType FROM yaha_pdi WHERE ioType LIKE 'SD%'")
    records = YahaPDIcursor.fetchall()

    #set record index for better readability
    processTag = 0
    ioType = 1

    if records is None:
        print('No process tags found')
    else:
        for record in records:
            tagList[record[processTag]] = record[ioType] #"tag" : ioType
                 
    return(tagList)





#get all different owners of PDI tags (e.g. used for IO-scheduler)
def YahaPDIgetDeviceIDs(owner):
    deviceIDlist = {'empty': 0}    #force creating a dictionary
    deviceIDlist.clear()           #clear dictionary immediately

    YahaPDIcursor.execute('''SELECT processTag, deviceID FROM yaha_pdi WHERE owner LIKE ?''', (owner+'%',))
    records = YahaPDIcursor.fetchall()

    processTag = 0
    deviceID   = 1

    if records is None:
        print('No process tags found')
    else:
        for record in records:
            deviceIDlist[record[processTag]] = record[deviceID] #"tag" : ID
                 
    return(deviceIDlist)

#get all different channels of PDI tags (e.g. used for IO-scheduler)
def YahaPDIgetHostChannels(owner):
    channelList = {'empty': 0}    #force creating a dictionary
    channelList.clear()           #clear dictionary immediately

    YahaPDIcursor.execute('''SELECT processTag, owner FROM yaha_pdi WHERE owner LIKE ?''', (owner+'%',))
    records = YahaPDIcursor.fetchall()

    processTag = 0
    owner   = 1

    if records is None:
        print('No process tags found')
    else:
        for record in records:
            try:
                channelList[record[processTag]] = record[owner].split('.')[1] #"tag" : owner.01 => tag : 01 
            except:
                channelList[record[processTag]] = None   #no specific host ID defined => use base ID in driver later on
                 
                 
    return(channelList)




class ProcessDataImage:
    'Yaha Process Data Image: simplifies handing central process data by using class attributes instead of dictionary strings'

    #creates the database holding the process data image
    def __init__(self):
        #
        self.pidProcessTagListTotal = {'empty': 0}    #force creating a dictionary
        self.pidProcessTagListTotal.clear()           #clear dictionary immediately
        
        #create Process Data Image
        YahaPDIcreate()

    #add items to PDI and initializes them
    def addItemsFromFile(self, pdiDefinitionFile):
        processTags = dict()
        processTags = YahaPDIaddItemsFromFile(pdiDefinitionFile)

        #dynamically add process tags to class as attributes and set init value
        for tag in processTags:
            setattr(self, tag, processTags[tag])

        #refresh list containing all PDI process tags
        self.pidProcessTagListTotal = YahaGetProcessTagListWithValue()

    #reads current values from the database and updates the PDI class object
    def read(self):
        processTags = {'empty': 0}    #force creating a dictionary
        processTags.clear()           #clear dictionary immediately

        #read all PDI tags: mark them with read flat: $read$
        for tag in self.pidProcessTagListTotal:
            processTags[tag] = "$read$"

        #read process variables from PDI
        processTags = YahaPDIreadValue(processTags, {})

        #set class variables with values from PDI
        for tag in processTags:
            setattr(self, tag, processTags[tag])

    #writes values from the class object to the database
    def write(self):
        processTags = {'empty': 0}    #force creating a dictionary
        processTags.clear()           #clear dictionary immediately

        #convert class variables into dictionary for PDI write
        for tag in self.pidProcessTagListTotal:
            processTags[tag] = getattr(self, tag)

        #write process variables from PDI
        YahaPDIwriteValue(processTags, {})

    def getTagOwners(self):
        return(YahaPDIgetOwners())
    
    def getTagDeviceIDs(self, owner):
        return(YahaPDIgetDeviceIDs(owner))

    def getTagHostChannels(self, owner):
        return(YahaPDIgetHostChannels(owner))

    def getTagStandardDeviceTags(self):
        return(YahaPDIgetStandardDeviceTags())


    

