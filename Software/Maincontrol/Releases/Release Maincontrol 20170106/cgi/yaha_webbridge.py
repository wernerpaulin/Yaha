#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cgi
import cgitb; cgitb.enable()
import datetime, threading, time
import time                 # Import 'time' library.  Allows us to use 'sleep'
import socket               # Import socket module
import json

#convert CGI field storage to JSON (via dictionary as JSON can not directly interpret CGI data
def cgiToJSON( fieldStorage ):
   #convert CGI data to Python dictionary
   cgiDict = {}
   for key in fieldStorage.keys():
    cgiDict[key] = fieldStorage[key].value
   
   #convert dictionary to JSON string
   return json.dumps(cgiDict) 
 
IP_ADR = "127.0.0.1"
PORT_Client_to_Server = 10000
PORT_Server_to_Client = 10001
RX_TX_BUFFER_SIZE = 4096
 
RXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
RXsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
RXsocket.bind((IP_ADR, PORT_Server_to_Client))
RXsocket.settimeout(2)  #1s timeout
#socket.setblocking(False) #non-blocking not used because we need to wait for a reply from server

TXsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#convert CGI fields to JSON for forwarding to server via UDP
jsonDataStream = cgiToJSON( cgi.FieldStorage() )
#send data to server via UDP
TXsocket.sendto(jsonDataStream, (IP_ADR, PORT_Client_to_Server))

#prepare reply
print "Content-type:text/html\r\n"  #mandatory header for CGI call backs
#timeout configured to avoid deadlock in case server is down and does not reply to sent message
try:
    #wait for reply
    jsonDataStream, addr = RXsocket.recvfrom(RX_TX_BUFFER_SIZE)

#in case of a configured timeout or non-blocking mode try-statement mandatory
except socket.error, e:
    RXsocket.close()
    TXsocket.close()
    #print e

# got a message
else:
    print jsonDataStream
    RXsocket.close()
    TXsocket.close()    
