#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

 # Create a database in RAM
db = sqlite3.connect(':memory:')

# Get a cursor object
cursor = db.cursor()
cursor.execute('''CREATE TABLE yaha_pdi(
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


cursor = db.cursor()

# Insert entries in process data image
pdiRecords = [("switch1","uiSwitch1","REAL", 0, "", "Main Control","enocean","ID123456","w",0.0,1.0,"GF","Family","Living room","light"),
              ("light1","uiLight1","REAL", 0, "", "Main Control","enocean","ID123457","r",0.0,1.0,"GF","Family","Living room","light"),
              ("tempParentBathroom","uiTempParentBathroom","REAL", 22.4, "", "Main Control","enocean","ID99999","r",0.0,0.0,"1F","Parents","Bathroom Parents","temperature"),
              ("setTempFelix","uiSetTempFelix","REAL", 22.4, "", "Main Control","enocean","ID99999","rw",0.0,40.0,"1F","Kids","Felix","temperature"),
              ("setTempTheo","uiSetTempTheo","REAL", 22.4, "", "Main Control","enocean","ID99999","rw",0.0,40.0,"1F","Kids","Theo","temperature"),
              ("logEnocean","uiLogEnocean","TEXT", 0, "Test log entry", "Main Control","internal","","r",0.0,0.0,"Driver","","","debugging")
              ]

cursor.executemany('''INSERT INTO yaha_pdi(processTag, 
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
                  pdiRecords)
"""
#Insert dictionary values
cursor.execute('''INSERT INTO yaha_pdi(name, phone, email, password)
                  VALUES(:name,:phone, :email, :password)''',
                  {'name':name1, 'phone':phone1, 'email':email1, 'password':password1})
"""

db.commit()
#Update data
cursor.execute('''UPDATE yaha_pdi SET valueREAL = ? WHERE processTag = ? ''',(99.99, "setTempFelix"))
  
db.commit()


#Retrieving Data (SELECT) with SQLite
#cursor.execute('''SELECT processTag, valueREAL, uiMode FROM yaha_pdi WHERE uiMode = "r" or uiMode = "rw"''')
cursor.execute('''SELECT processTag, valueREAL, uiMode FROM yaha_pdi WHERE processTag="light1" AND (uiMode = "r" OR uiMode = "rw")''')
for row in cursor:
    # row[0]: processTag, row[1]: valueREAL, row[2]: uiMode
    print('{0} : {1}, {2}'.format(row[0], row[1], row[2]))
    


# Close the db connection
db.close()
