#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()
import datetime, threading, time
import time ## Import 'time' library.  Allows us to use 'sleep'
import socket               # Import socket module
import json

IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001


RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
RXsocket.bind((IP_ADR, PORT_Server_to_Client))

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#convert CGI field storage to JSON (via dictionary as json can not directly interpret CGI data
def cgiToJSON( fieldStorage ):
   #convert CGI data to Python dictionary
   cgiDict = {}
   for key in fieldStorage.keys():
      cgiDict[key] = fieldStorage[key].value
   
   #convert dictionary to JSON string
   return json.dumps(cgiDict) 


#direct forward of browser data to server as json
jsonString = cgiToJSON( cgi.FieldStorage() )

#Generisch auspacken und gem. Tagliste auf Variablen schreiben   
dataFromClient = []
dataFromClient = json.loads(jsonString)

#create UI mapping to process data - SPÄTER XML
UImapping = {}
UImapping['spanOutput1']    = 'textOut1'
UImapping['spanOutput2']    = 'textOut2'
UImapping['checkboxgroup1'] = 'chk1'
UImapping['checkboxgroup2'] = 'chk2'
UImapping['radiogroup1']    = 'rd1'
UImapping['radiogroup2']    = 'rd2'
UImapping['selectStandard'] = 'select1'
UImapping['selectGroup']    = 'select2'
UImapping['inputSetValue1']    = 'textIn1'
UImapping['inputSetValue2']    = 'textIn2'



ProcessDataImage = {}
ProcessDataImage['textOut1']['value'] = "val textOut1" 
ProcessDataImage['textOut1']['rw'] = "r" 
ProcessDataImage['textOut1']['low'] = "" 
ProcessDataImage['textOut1']['high'] = "" 

ProcessDataImage['textOut2']['value'] = "val textOut2" 
ProcessDataImage['textOut2']['rw'] = "r" 
ProcessDataImage['textOut2']['low'] = "" 
ProcessDataImage['textOut2']['high'] = "" 

ProcessDataImage['textIn1']['value'] = "val textIn1" 
ProcessDataImage['textIn1']['rw'] = "rw" 
ProcessDataImage['textIn1']['low'] = "" 
ProcessDataImage['textIn1']['high'] = "" 

ProcessDataImage['textIn2']['value'] = "val textIn2" 
ProcessDataImage['textIn2']['rw'] = "rw" 
ProcessDataImage['textIn2']['low'] = "" 
ProcessDataImage['textIn2']['high'] = "" 

ProcessDataImage['txtLogOutput']['value'] = "val txtLogOutput" 
ProcessDataImage['txtLogOutput']['rw'] = "rw" 
ProcessDataImage['txtLogOutput']['low'] = "" 
ProcessDataImage['txtLogOutput']['high'] = "" 




"""
testDict['checkboxgroup1'] = False
testDict['checkboxgroup2'] = True
testDict['radiogroup1'] = False
testDict['radiogroup2'] = True
testDict['selectStandard'] = "Select3"
testDict['selectGroup'] = "Select2G2"
"""

for key in dataFromClient:
    #get corresponding process data tag to UI tag
    uiTag = dataFromClient[key]
        
    if uiTag in ProcessDataImage:
        ProcessDataImage[uiTag]
     
    if ProcessDataImage[dataFromClient[key]][]




jsonString = json.dumps(dataToServer)
print "Content-type:text/html\r\n"
print jsonString



"""
#CGI daten in dictionary generisch umwandeln
txData = {"page":"logEnOcean", "reset": "False"}
    
TXsocket.sendto(json.dumps(txData), (IP_ADR, PORT_Client_to_Server))
rxData, addr = RXsocket.recvfrom(1024) # buffer size is 1024 bytes

print "Content-type:text/html\r\n"
print rxData #forward data web browser for further processing

RXsocket.close()
TXsocket.close()
"""
