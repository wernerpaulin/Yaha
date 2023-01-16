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
testDict = []
testDict = json.loads(jsonString)
testDict['spanOutput2'] = testDict['inputSetValue1'] + testDict['inputSetValue2']
testDict['spanOutput1'] = "Test from server"
testDict['checkboxgroup1'] = False
testDict['checkboxgroup2'] = True
testDict['radiogroup1'] = False
testDict['radiogroup2'] = True
testDict['radiogroup2'] = True
testDict['radiogroup2'] = True
testDict['selectStandard'] = "Select3"
testDict['selectGroup'] = "Select2G2"


jsonString = json.dumps(testDict)
print "Content-type:text/html\r\n"
print jsonString
#for key in testDict:
#    print key



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
