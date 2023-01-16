#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import xml.etree.ElementTree as xmlParser
import os

def YahaPDIcreate(xmlDefinitionFile):
    global YahaPDIcursor

    # Create a database in RAM
    db = sqlite3.connect(':memory:')
    
    # Get a cursor object
    YahaPDIcursor = db.cursor()
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
    db.commit()
    
    #get access to data base
    YahaPDIcursor = db.cursor()

    #read process data image configuration from xml file
    pdiRecord = {'empty': 0}    #force creating a dictionary
    pdiRecord.clear()           #clear dictionary immediately
    pdiTree = xmlParser.parse('/home/pi/Yaha/yaha_pdi.xml')
    pdiRoot = pdiTree.getroot()
    
    #walk through all process data elements in process data image
    for process_data in pdiRoot:
        #read out all properties (= sub children) into a dictionary
        pdiRecord.clear()   #clear dictionary from data from last loop
        for property in process_data:
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
        
        db.commit()


def YahaPDIwrite(processTag, uiTag, dictData):
    
    
#EXAMPLE: write data
cursor.execute('''UPDATE yaha_pdi SET valueREAL = ? WHERE processTag = ? ''',(99.99, "setTempFelix"))
db.commit()


#EXAMPLE: read data
YahaPDIcursor.execute('''SELECT processTag, valueREAL, uiMode FROM yaha_pdi WHERE uiMode = "r" or uiMode = "rw"''')
#YahaPDIcursor.execute('''SELECT processTag, valueREAL, uiMode FROM yaha_pdi WHERE ioType="light" AND (uiMode = "r" OR uiMode = "rw")''')
for row in YahaPDIcursor:
    # row[0]: processTag, row[1]: valueREAL, row[2]: uiMode
    print('{0} : {1}, {2}'.format(row[0], row[1], row[2]))
    


# Close the db connection
db.close()

"""
#EXAMPLE: list files in directory (e.g. for receipe handling)
path = '/home/pi/Yaha'
for dirname, dirnames, filenames in os.walk(path):
    # print path to all filenames with extension py.
    for filename in filenames:
        fname_path = os.path.join(dirname, filename)
        fext = os.path.splitext(fname_path)[1]
        if fext == '.xml':
            print fname_path
        else:
            continue
    break   #search only top directory (remove break to walk also all sub folders
"""

